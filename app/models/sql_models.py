from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base  # Importing the Base class we created earlier


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    borrows = relationship("Borrow", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    isbn = Column(String, unique=True, index=True)

    # Content Layer (Assignment Requirement: Manage actual files)
    file_path = Column(String, nullable=False)  # Path to local file or S3 key
    file_type = Column(String, default="pdf")  # pdf or txt

    # Intelligence Layer (Assignment Requirement: AI Summaries)
    summary = Column(Text, nullable=True)  # AI generated summary
    sentiment_score = Column(Float, default=0.0)  # Rolling avg of review sentiments

    borrows = relationship("Borrow", back_populates="book")
    reviews = relationship("Review", back_populates="book")


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(DateTime(timezone=True), server_default=func.now())
    return_date = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")


class UserPreference(Base):
    """
    Design Decision for ML:
    Storing preferences as JSON allows us to be flexible with our ML algorithm.
    We can store explicit tags (e.g., {"genres": ["sci-fi"]})
    or implicit vectors (e.g., {"embedding": [0.12, -0.4, ...]})
    without migrating the DB.
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    topic_tag = Column(String)  # e.g., "Fiction", "Science", "History"
    # Flexible schema for ML data using JSON
    # Note: We use JSON instead of JSONB for compatibility with all Postgres versions
    data = Column(JSON, default={})

    user = relationship("User", back_populates="preferences")
