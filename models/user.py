from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class PromotionLevel(str, Enum):
    LICENCE = "licence"
    MASTER = "master"
    DOCTORAT = "doctorat"
    PROF = "prof"

class Mention(str, Enum):
    INFORMATIQUE = "informatique"
    MATH = "math"
    AUTRE = "autre"

class UserBase(BaseModel):
    clerk_id: str = Field(..., description="Clerk user ID")
    name: str = Field(..., description="User's full name")
    promotion: PromotionLevel = Field(..., description="User's academic level")
    mention: Mention = Field(..., description="User's academic major")
    email: str = Field(None, description="User's email address")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="User's full name")
    promotion: Optional[PromotionLevel] = Field(None, description="User's academic level")
    mention: Optional[Mention] = Field(None, description="User's academic major")
    email: Optional[str] = Field(None, description="User's email address")

