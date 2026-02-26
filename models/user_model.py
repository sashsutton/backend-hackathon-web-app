from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class UserBase(BaseModel):
    clerk_id: str = Field(..., description="Clerk user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    promotion: str = Field(..., description="User's academic level")
    mention: str = Field(..., description="User's academic major")
    email: str = Field(None, description="User's email address")
    elo: int = Field(1200, description="User's ELO rating")
    total_duels: int = Field(0, description="Total duels played")
    wins: int = Field(0, description="Total wins")
    losses: int = Field(0, description="Total losses")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="User's full name")
    promotion: Optional[str] = Field(None, description="User's academic level")
    mention: Optional[str] = Field(None, description="User's academic major")
    email: Optional[str] = Field(None, description="User's email address")

