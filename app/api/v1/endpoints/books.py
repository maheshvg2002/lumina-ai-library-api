import uuid
from pathlib import Path

from app.api.dependencies import get_llm_service, get_storage_service
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user

from app.core.interfaces import LLMProvider, StorageProvider
from app.db.session import get_db
from app.domain import schemas
from app.models.sql_models import Book, User

router = APIRouter()


async def process_ai_summary(book_id: int, file_path: str, db_gen, llm: LLMProvider):
    # 1. Read the uploaded file
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 2. Call the injected LLM Provider (It doesn't know if it's Ollama or OpenAI!)
        summary = await llm.generate_summary(content)

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
    current_user: User = Depends(get_current_user),
    storage: StorageProvider = Depends(get_storage_service),
    llm: LLMProvider = Depends(get_llm_service),
):
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Only PDF or TXT allowed")

    # Generate a unique filename safely
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    content = await file.read()

    file_path = await storage.save_file(unique_filename, content)

    new_book = Book(
        title=title,
        author=author,
        isbn=isbn,
        file_path=str(file_path),
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    background_tasks.add_task(
        process_ai_summary, new_book.id, str(file_path), get_db, llm
    )

    return new_book


@router.get("/", response_model=list[schemas.BookResponse])
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Book).offset(skip).limit(limit).all()
