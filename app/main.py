from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.api.v1.endpoints import auth, books, interactions # NEW

# 1. Initialize the API
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 2. Register the Routers
# This adds the /signup and /login endpoints under the /api/v1/auth prefix
app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_STR}/auth", 
    tags=["Authentication"]
)

# 3. Root / Health Check Endpoint
@app.get("/")
def health_check(db: Session = Depends(get_db)):
    """
    Root endpoint to test if the API is running and 
    can connect to the database.
    """
    try:
        # Attempt a simple SQL query to verify connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "system": "LuminaLib",
            "database": "connected",
            "message": "System is ready for requests."
        }
    except Exception as e:
        # If DB is down, return a 500 error with details
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )
        
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(books.router, prefix=f"{settings.API_V1_STR}/books", tags=["Books"]) 
app.include_router(interactions.router, prefix=f"{settings.API_V1_STR}/interactions", tags=["Interactions"])

# 4. (Optional) Run directly for debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)