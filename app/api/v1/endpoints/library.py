from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.models.sql_models import Borrow, Book, User
# We will assume you have a 'get_current_user' dependency for security
from app.api.v1.endpoints.auth import get_current_user 

router = APIRouter()

@router.post("/{book_id}/borrow")
def borrow_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check if book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 2. Check if already borrowed and not returned
    existing_borrow = db.query(Borrow).filter(
        Borrow.book_id == book_id, 
        Borrow.user_id == current_user.id,
        Borrow.return_date == None
    ).first()
    
    if existing_borrow:
        raise HTTPException(status_code=400, detail="You already have this book")

    # 3. Create borrow record
    new_borrow = Borrow(user_id=current_user.id, book_id=book_id)
    db.add(new_borrow)
    db.commit()
    return {"message": f"Successfully borrowed '{book.title}'"}

@router.post("/{book_id}/return")
def return_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    borrow_record = db.query(Borrow).filter(
        Borrow.book_id == book_id,
        Borrow.user_id == current_user.id,
        Borrow.return_date == None
    ).first()

    if not borrow_record:
        raise HTTPException(status_code=400, detail="No active borrow record found")

    borrow_record.return_date = datetime.utcnow()
    db.commit()
    return {"message": "Book returned successfully"}