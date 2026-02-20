from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.sql_models import Review, Borrow, User
from app.domain import schemas
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/{book_id}/reviews")
def post_review(
    book_id: int,
    review_in: schemas.ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # CONSTRAINT: Check if user ever borrowed this book 
    has_borrowed = db.query(Borrow).filter(
        Borrow.book_id == book_id,
        Borrow.user_id == current_user.id
    ).first()

    if not has_borrowed:
        raise HTTPException(
            status_code=403, 
            detail="You must borrow the book before reviewing it."
        )

    new_review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(new_review)
    db.commit()

    # TRIGGER ASYNC TASK: Analyze sentiment [cite: 24]
    # background_tasks.add_task(analyze_sentiment_task, book_id, review_in.comment)
    
    return {"message": "Review submitted successfully"}