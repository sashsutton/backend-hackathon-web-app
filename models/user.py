from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class UserBase(BaseModel):
    clerk_id: str = Field(..., description="Clerk user ID")
    name: str = Field(..., description="User's full name")
    promotion: str = Field(..., description="User's academic level")
    mention: str = Field(..., description="User's academic major")
    email: str = Field(None, description="User's email address")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="User's full name")
    promotion: Optional[str] = Field(None, description="User's academic level")
    mention: Optional[str] = Field(None, description="User's academic major")
    email: Optional[str] = Field(None, description="User's email address")

