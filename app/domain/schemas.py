from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# 1. Shared properties
class UserBase(BaseModel):
    email: EmailStr


# 2. Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None


# 3. Properties to return to client (NEVER return password)
class UserResponse(UserBase):
    id: int
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# 4. Token Schema (for Login response)
class Token(BaseModel):
    access_token: str
    token_type: str


class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    file_path: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True


# Borrow Schemas
class BorrowCreate(BaseModel):
    book_id: int


class BorrowResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Review Schemas
class ReviewCreate(BaseModel):
    book_id: int
    rating: int
    comment: str


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    comment: str
    sentiment: Optional[str] = "Pending"
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True
