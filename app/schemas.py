
from pydantic import (
    BaseModel, Field, ConfigDict, EmailStr
)
from typing import Literal
from pydantic import Field


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    skills: list[str]
    experience: int = Field(ge=0)


class CandidateResponse(CandidateCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)



class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    company: str = Field(min_length=1, max_length=150)
    location: str = Field(min_length=1, max_length=100)
    required_experience: int = Field(ge=0)
    required_skills: list[str] = Field(
        default_factory=list
    )


class JobResponse(JobCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)



class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: Literal["admin", "hr", "candidate"]

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
