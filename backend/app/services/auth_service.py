"""
auth_service.py - Business logic service for user authentication,
credential verification, token issuance, and security auditing.
Separated from the HTTP router layer.
"""

from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.schema_models import User
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    decode_access_token,
    validate_password_complexity,
)
from app.core.logging import is_rate_limited, log_login_attempt

# Known demo credentials for academic prototype convenience
DEMO_PASSWORDS = {
    "rahul.sharma@oksbi": "Customer#2026",
    "fresh.mart@paytm": "Merchant#2026",
    "analyst@payguard.ai": "Admin@Secure2026",
    "vikram.singh@payguard.ai": "Admin@Secure2026",
    "priya.patel@okaxis": "Customer#2026",
    "amit.kumar@ybl": "Customer#2026",
    "sneha.reddy@barodampay": "Customer#2026",
}


class AuthService:
    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str,
        client_ip: str,
    ) -> Tuple[User, str]:
        """
        Validates user credentials against brute-force limits, complexity, and database records.
        Returns (user, access_token).
        """
        clean_email = email.strip().lower()

        # 1. Rate Limiting Check
        locked, retry_after = is_rate_limited(clean_email, client_ip)
        if locked:
            log_login_attempt(
                identifier=clean_email,
                client_ip=client_ip,
                success=False,
                reason=f"Account locked. Rate limit exceeded (retry after {retry_after}s)",
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Account locked for {retry_after} seconds.",
            )

        # 2. Server-side Password Complexity Check
        is_valid_complexity, complexity_error = validate_password_complexity(password)
        if not is_valid_complexity:
            log_login_attempt(
                identifier=clean_email,
                client_ip=client_ip,
                success=False,
                reason=f"Rejected: {complexity_error}",
            )
            # Never leak exact password rules or email existence - return generic credential failure
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        # 3. Database User Lookup (case-insensitive email or UPI identifier)
        user = (
            db.query(User)
            .filter(User.email.ilike(clean_email))
            .first()
        )

        if not user:
            log_login_attempt(
                identifier=clean_email,
                client_ip=client_ip,
                success=False,
                reason="User not found in database",
            )
            # Generic error to prevent user enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        # 4. Password Hash Verification
        is_valid_password = False

        # Check standard bcrypt hash
        if user.passwordHash and verify_password(password, user.passwordHash):
            is_valid_password = True
        elif clean_email in DEMO_PASSWORDS and password == DEMO_PASSWORDS[clean_email]:
            # Seamlessly upgrade legacy/demo hash to real bcrypt hash
            is_valid_password = True
            try:
                user.passwordHash = hash_password(password)
                db.commit()
            except Exception:
                db.rollback()

        if not is_valid_password:
            log_login_attempt(
                identifier=clean_email,
                client_ip=client_ip,
                success=False,
                reason="Invalid password mismatch",
                user_id=user.userId,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        # 5. Success: log audit trail and issue JWT
        log_login_attempt(
            identifier=clean_email,
            client_ip=client_ip,
            success=True,
            user_id=user.userId,
        )

        role_normalized = "customer"
        if user.role.upper() in ["ADMIN", "ANALYST"]:
            role_normalized = "admin"
        elif user.role.lower() == "merchant" or "merchant" in user.name.lower() or "merchant" in user.email.lower():
            role_normalized = "merchant"

        token = create_access_token(
            data={
                "sub": str(user.userId),
                "email": user.email,
                "name": user.name,
                "role": role_normalized,
            }
        )

        return user, token

    def get_current_user_from_token(self, db: Session, token: str) -> User:
        """Decodes JWT bearer token and resolves the user entity."""
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token.",
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token payload.",
            )

        user = db.query(User).filter(User.userId == int(user_id_str)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user no longer exists.",
            )

        return user


auth_service = AuthService()
