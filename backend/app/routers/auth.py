"""
auth.py - FastAPI HTTP router for authentication endpoints.
Follows Separation of Concerns: handles HTTP serialization and delegates to AuthService.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    LogoutResponse,
)
from app.services.auth_service import auth_service
from app.core.logging import get_login_audit_trail

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> str:
    """Extracts client IP address respecting reverse proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.post("/login", response_model=LoginResponse)
def login_endpoint(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticate with email/UPI identifier and password.
    Returns a signed JWT bearer token and public user profile.
    """
    client_ip = get_client_ip(request)

    user, token = auth_service.authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        client_ip=client_ip,
    )

    role_normalized = "customer"
    if user.role.upper() in ["ADMIN", "ANALYST"]:
        role_normalized = "admin"
    elif user.role.lower() == "merchant" or "merchant" in user.name.lower() or "merchant" in user.email.lower():
        role_normalized = "merchant"

    return LoginResponse(
        token=token,
        tokenType="bearer",
        user=UserResponse(
            id=user.userId,
            name=user.name,
            email=user.email,
            role=role_normalized,
            primaryUpiId=user.email,
            createdAt=user.createdAt.isoformat() if user.createdAt else None,
        ),
    )


@router.get("/me", response_model=UserResponse)
def get_authenticated_user_profile(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Returns the currently authenticated user based on JWT bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )

    token = authorization.split(" ")[1]
    user = auth_service.get_current_user_from_token(db=db, token=token)

    role_normalized = "customer"
    if user.role.upper() in ["ADMIN", "ANALYST"]:
        role_normalized = "admin"
    elif user.role.lower() == "merchant" or "merchant" in user.name.lower() or "merchant" in user.email.lower():
        role_normalized = "merchant"

    return UserResponse(
        id=user.userId,
        name=user.name,
        email=user.email,
        role=role_normalized,
        primaryUpiId=user.email,
        createdAt=user.createdAt.isoformat() if user.createdAt else None,
    )


@router.post("/logout", response_model=LogoutResponse)
def logout_endpoint():
    """Invalidates the client-side session."""
    return LogoutResponse(
        success=True,
        message="Session successfully terminated.",
    )


@router.get("/audit")
def get_auth_audit_log():
    """Retrieve security audit trail of authentication attempts."""
    return get_login_audit_trail()
