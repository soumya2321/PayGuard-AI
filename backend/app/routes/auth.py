"""
auth.py - Production authentication and JWT token management endpoints for PayGuard AI.
Implements secure password verification (bcrypt), brute-force rate-limiting, and session validation.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema_models import User
from app.core.security import verify_password, create_access_token, decode_access_token
from app.core.logging import is_rate_limited, log_login_attempt, get_login_audit_trail

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    primaryUpiId: Optional[str] = None
    createdAt: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    tokenType: str = "Bearer"
    user: UserResponse


def normalize_role(db_role: str) -> str:
    """Maps database uppercase roles to frontend UserRole: 'customer' | 'merchant' | 'admin'."""
    r = (db_role or "USER").upper()
    if r == "ADMIN":
        return "admin"
    if r == "MERCHANT":
        return "merchant"
    return "customer"


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticates user credentials, applies rate limiting, and issues JWT access token.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    clean_identifier = payload.email.strip().lower()

    # 1. Check rate-limit lockout
    locked, retry_after = is_rate_limited(clean_identifier, client_ip)
    if locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Account locked for {retry_after} seconds.",
        )

    # 2. Look up user by email or upi handle
    user = (
        db.query(User)
        .filter(
            (User.email.ilike(clean_identifier))
            | (User.email.ilike(f"{clean_identifier}%"))
        )
        .first()
    )

    if not user:
        log_login_attempt(clean_identifier, client_ip, success=False, reason="User identifier not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify credentials.",
        )

    # 3. Verify password hash
    is_valid = verify_password(payload.password, user.passwordHash)
    if not is_valid:
        log_login_attempt(clean_identifier, client_ip, success=False, reason="Invalid password", user_id=user.userId)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify credentials.",
        )

    # 4. Successful Authentication
    log_login_attempt(clean_identifier, client_ip, success=True, user_id=user.userId)

    role_str = normalize_role(user.role)
    token_claims = {
        "sub": str(user.userId),
        "email": user.email,
        "name": user.name,
        "role": role_str,
    }
    jwt_token = create_access_token(token_claims)

    user_payload = UserResponse(
        id=user.userId,
        name=user.name,
        email=user.email,
        role=role_str,
        primaryUpiId=user.email,
        createdAt=user.createdAt.isoformat() if user.createdAt else datetime.now(timezone.utc).isoformat(),
    )

    return LoginResponse(
        token=jwt_token,
        tokenType="Bearer",
        user=user_payload,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Validates bearer token and returns authenticated user profile.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )

    token = authorization.split(" ")[1]
    claims = decode_access_token(token)
    if not claims or "sub" not in claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token invalid. Please log in again.",
        )

    user_id = int(claims["sub"])
    user = db.query(User).filter(User.userId == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user profile not found.",
        )

    return UserResponse(
        id=user.userId,
        name=user.name,
        email=user.email,
        role=normalize_role(user.role),
        primaryUpiId=user.email,
        createdAt=user.createdAt.isoformat() if user.createdAt else datetime.now(timezone.utc).isoformat(),
    )


@router.post("/logout")
async def logout():
    """
    Terminates authenticated session.
    """
    return {
        "success": True,
        "message": "Session terminated successfully.",
    }


@router.get("/audit")
async def get_audit_trail():
    """
    Returns recent authentication audit trail.
    """
    return {
        "trail": get_login_audit_trail(),
    }
