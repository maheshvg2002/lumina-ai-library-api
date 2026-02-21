from datetime import datetime
from typing import List

from app.api.dependencies import get_llm_service
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api.v1.endpoints.auth import get_current_user

# --- CLEAN ARCHITECTURE IMPORTS ---
from app.core.interfaces import LLMProvider
from app.db.session import get_db
from app.domain import schemas
from app.infrastructure.services.ml_service import RecommendationEngine
from app.models.sql_models import Book, Borrow, Review, User, UserPreference

router = APIRouter()

# Initialize the ML Engine once so it doesn't reload on every request
ml_engine = RecommendationEngine()


# --- UPDATE 1: Pass the LLMProvider into the background task ---
async def process_review_sentiment(
    review_id: int, review_text: str, db_gen, llm: LLMProvider
):
    try:
        # It no longer uses a global variable, it uses the injected service!
        sentiment = await llm.analyze_sentiment(review_text)

        # Update Database
        db = next(db_gen())
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            review.sentiment = sentiment
            db.commit()
    except Exception as e:
        print(f"Sentiment Analysis Failed: {e}")


# --- BORROWING ---


@router.post("/borrow/", response_model=schemas.BorrowResponse)
def borrow_book(
    borrow_data: schemas.BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Check if book exists
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. Check if already borrowed and not returned
    active_borrow = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == borrow_data.book_id,
            Borrow.user_id == current_user.id,
            Borrow.return_date == None,
        )
        .first()
    )

    if active_borrow:
        raise HTTPException(
            status_code=400, detail="You have already borrowed this book."
        )

    # 3. Create Borrow Record
    new_borrow = Borrow(user_id=current_user.id, book_id=borrow_data.book_id)
    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)
    return new_borrow


@router.post("/return/{borrow_id}", response_model=schemas.BorrowResponse)
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow_record = (
        db.query(Borrow)
        .filter(Borrow.id == borrow_id, Borrow.user_id == current_user.id)
        .first()
    )
    if not borrow_record:
        raise HTTPException(status_code=404, detail="Borrow record not found")

    borrow_record.return_date = datetime.utcnow()
    db.commit()
    db.refresh(borrow_record)
    return borrow_record


# --- REVIEWS ---


@router.post("/reviews/", response_model=schemas.ReviewResponse)
def create_review(
    review_data: schemas.ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # --- UPDATE 2: Inject the LLM Service ---
    llm: LLMProvider = Depends(get_llm_service),
):
    # 1. Validate Rating
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # 2. **CRITICAL RULE**: User must have borrowed the book at least once
    has_borrowed = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == review_data.book_id, Borrow.user_id == current_user.id
        )
        .first()
    )

    if not has_borrowed:
        raise HTTPException(
            status_code=403, detail="You must borrow a book before reviewing it."
        )

    # 3. Check if already reviewed (Optional rule: 1 review per book)
    existing_review = (
        db.query(Review)
        .filter(
            Review.book_id == review_data.book_id, Review.user_id == current_user.id
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=400, detail="You have already reviewed this book."
        )

    new_review = Review(
        user_id=current_user.id,
        book_id=review_data.book_id,
        rating=review_data.rating,
        comment=review_data.comment,
        sentiment="Pending",
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # --- UPDATE 3: Pass the injected LLM to the background task ---
    background_tasks.add_task(
        process_review_sentiment, new_review.id, new_review.comment, get_db, llm
    )
    return new_review


@router.get("/reviews/{book_id}", response_model=List[schemas.ReviewResponse])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.book_id == book_id).all()


@router.get("/recommendations/", response_model=list[schemas.RecommendationResponse])
def get_ml_recommendations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # 1. Get IDs of books the user has already borrowed
    borrowed_books = (
        db.query(Borrow.book_id).filter(Borrow.user_id == current_user.id).all()
    )
    borrowed_book_ids = [b[0] for b in borrowed_books]

    # 2. Gather the text to build the "User ML Profile"
    user_profile_text = []

    # A. Add summaries of books they've read
    if borrowed_book_ids:
        liked_books = db.query(Book).filter(Book.id.in_(borrowed_book_ids)).all()
        for book in liked_books:
            if book.summary and book.summary != "Pending...":
                user_profile_text.append(book.summary)

    # B. Add Explicit User Preferences (e.g., "Sci-Fi", "Machine Learning")
    explicit_prefs = (
        db.query(UserPreference.topic_tag)
        .filter(UserPreference.user_id == current_user.id)
        .all()
    )
    for pref in explicit_prefs:
        user_profile_text.append(pref[0])

    # 3. Handle the "Cold Start" (User is brand new, no history, no prefs)
    if not user_profile_text:
        # Fallback: Just return the Top 5 highest-rated books overall
        fallback_recommendations = (
            db.query(Book)
            .outerjoin(Review, Book.id == Review.book_id)
            .filter(Book.id.notin_(borrowed_book_ids) if borrowed_book_ids else True)
            .group_by(Book.id)
            .order_by(func.coalesce(func.avg(Review.rating), 0).desc())
            .limit(1)
            .all()
        )
        return fallback_recommendations

    # 4. Prepare the unread books for the ML Model
    if borrowed_book_ids:
        other_books_query = (
            db.query(Book).filter(Book.id.notin_(borrowed_book_ids)).all()
        )
    else:
        other_books_query = db.query(Book).all()

    all_other_books = [
        {"id": b.id, "title": b.title, "summary": b.summary}
        for b in other_books_query
        if b.summary and b.summary != "Pending..."
    ]

    # 5. Run the Content-Based ML Algorithm
    scored_results = ml_engine.get_content_based_recommendations(
        user_liked_summaries=user_profile_text, all_other_books=all_other_books
    )

    # 6. Fetch the actual Book objects from the DB using the ML winning IDs
    recommended_books = []
    for result in scored_results[:1]:  # Grab Top 5 ML Matches
        book = db.query(Book).filter(Book.id == result["book_id"]).first()
        if book:
            recommended_books.append(book)

    return recommended_books
