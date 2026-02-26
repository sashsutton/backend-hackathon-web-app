from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List




class UserBase(BaseModel):

    clerk_id: str = Field(..., description="Clerk user ID")
    first_name: str = Field(..., description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(..., description="User's last name", min_length=1, max_length=50)
    promotion: str = Field(..., description="User's academic level")
    mention: str= Field(..., description="User's academic major")
    email: EmailStr = Field(..., description="User's email address")
    elo_rating: int = Field(1200, description="User's ELO rating", ge=0, le=3000)
    total_duels: int = Field(0, description="Total duels played", ge=0)
    wins: int = Field(0, description="Total duels won", ge=0)
    losses: int = Field(0, description="Total duels lost", ge=0)

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):

    first_name: Optional[str] = Field(None, description="User's first name", min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, description="User's last name", min_length=1, max_length=50)
    promotion: Optional[str] = Field(None, description="User's academic level")
    mention: Optional[str] = Field(None, description="User's academic major")
    email: Optional[EmailStr] = Field(None, description="User's email address")

    class Config:
        from_attributes = True


class UserResponse(BaseModel):

    clerk_id: str = Field(..., description="Clerk user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    promotion: str = Field(..., description="User's academic level")
    mention: str = Field(..., description="User's academic major")
    email: EmailStr = Field(..., description="User's email address")
    elo_rating: int = Field(..., description="User's ELO rating")
    total_duels: int = Field(..., description="Total duels played")
    wins: int = Field(..., description="Total duels won")
    losses: int = Field(..., description="Total duels lost")
    win_rate: float = Field(..., description="Win rate percentage")

    class Config:
        from_attributes = True

