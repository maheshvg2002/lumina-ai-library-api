# LuminaLib - Intelligent Library System

LuminaLib is a next-generation, content-aware library system built for the JKTech Senior Backend & GenAI Engineer assessment. It moves beyond standard metadata CRUD operations by managing actual book files, utilizing a local LLM (via Ollama) to synthesize reader sentiment, and employing machine learning to drive personalized book discovery.

## Tech Stack
* **Backend:** Python 3.10, FastAPI, SQLAlchemy, Alembic
* **Database:** PostgreSQL 15
* **AI/ML:** Local LLM (Llama3 via Ollama), Scikit-Learn 
* **Infrastructure:** Docker, Docker Compose

## Quick Start (One-Command Deployment)

The application is fully containerized and designed to start with a single command. The `docker-compose.yml` handles the API, PostgreSQL database, and the local LLM service seamlessly.

1. **Clone the repository:**


-  git clone <your-repository-url>](https://github.com/maheshvg2002/lumina-ai-library-api.git)

-  cd luminalib


2. **Start the application:**
  
 - docker compose up --build
  
   *(Note: On the very first run, the `init-ollama` container will download the LLM weights. This may take a few minutes depending on your internet connection. The API will start automatically once the database is healthy).*

3. **Access the API Documentation:**
   Once the terminal displays `Application startup complete`, navigate to:
   * **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Core Features
* **Stateless Authentication:** Secure JWT-based signup and login flows.
* **True File Ingestion:** Upload actual book files (PDF/TXT) abstracted behind a storage interface.
* **Asynchronous AI Processing:** Non-blocking background tasks automatically generate book summaries upon upload and extract consensus sentiment from user reviews.
* **ML Recommendations:** Suggests books to users based on text vectorization of book summaries aligned with their interaction history and preferences.
