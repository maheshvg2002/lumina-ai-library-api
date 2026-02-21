from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import auth, books, interactions  # NEW
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get("/", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Root endpoint to test if the API is running and
    can connect to the database.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "system": "LuminaLib",
            "database": "connected",
            "message": "System is ready for requests.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


# Routers
app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"]
)
app.include_router(books.router, prefix=f"{settings.API_V1_STR}/books", tags=["Books"])
app.include_router(
    interactions.router,
    prefix=f"{settings.API_V1_STR}/interactions",
    tags=["Interactions"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
