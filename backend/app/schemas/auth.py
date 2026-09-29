"""
auth.py - Strict Pydantic schemas for authentication requests and responses.
No raw dictionaries used.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=120, description="User email or UPI identifier")
    password: str = Field(..., min_length=8, description="User secret password")


class UserResponse(BaseModel):
    id: int = Field(..., description="User unique integer ID")
    name: str = Field(..., description="Full user name")
    email: str = Field(..., description="Unique email or UPI handle")
    role: str = Field(..., description="User role: customer, merchant, or admin")
    primaryUpiId: Optional[str] = Field(None, description="Primary UPI VPA handle")
    createdAt: Optional[str] = Field(None, description="Account creation ISO timestamp")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Signed JWT access token")
    tokenType: str = Field("bearer", description="Token authentication scheme")
    user: UserResponse = Field(..., description="Authenticated user profile")


class LogoutResponse(BaseModel):
    success: bool = Field(True, description="Whether logout succeeded")
    message: str = Field(..., description="Status message")
