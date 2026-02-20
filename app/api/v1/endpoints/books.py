import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sql_models import Book, User
from app.domain import schemas
from app.api.v1.endpoints.auth import get_current_user
from app.infrastructure.services.ollama_service import OllamaService

router = APIRouter()
llm_service = OllamaService()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- BACKGROUND TASK ---
async def process_ai_summary(book_id: int, file_path: str, db_gen):
    # 1. Read the uploaded file
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # 2. Call Ollama
        summary = await llm_service.generate_summary(content)
        
        # 3. Update Database
        db = next(db_gen())
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            book.summary = summary
            db.commit()
    except Exception as e:
        print(f"Error in background AI task: {e}")

# --- ENDPOINTS ---

@router.post("/", response_model=schemas.BookResponse)
async def upload_book(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Only PDF or TXT allowed")

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_book = Book(
        title=title,
        author=author,
        isbn=isbn,
        file_path=str(file_path)
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # Trigger the AI Summary in the background
    background_tasks.add_task(process_ai_summary, new_book.id, str(file_path), get_db)

    return new_book

@router.get("/", response_model=list[schemas.BookResponse])
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Book).offset(skip).limit(limit).all()