# Architecture & Design Decisions: LuminaLib

This document outlines the architectural patterns, data models, and system design choices made for the LuminaLib platform. The system was designed with a focus on Clean Architecture, SOLID principles, and horizontal extensibility.

## 1. Clean Architecture & Interface-Driven Development
The application is structured in layers to decouple the business logic from the external frameworks (FastAPI), infrastructure (PostgreSQL), and third-party services (LLMs, Storage).

### Dependency Injection (DI)
FastAPI's dependency injection system is utilized globally. Database sessions, configuration settings, and external service clients are injected into the route handlers. This ensures that the application is easily testable and decoupled.

### Swappable Interfaces (The "Plugin" Architecture)
The architecture supports swapping components with minimal friction. This is achieved using Python `Protocols` / Abstract Base Classes:

* **Storage Abstraction:** File ingestion does not hardcode local file paths into the business logic. Instead, a `StorageBackend` interface is defined. Currently, it uses local storage, but switching to AWS S3 or MinIO simply requires writing a new class that implements the interface and updating the configuration.
* **LLM Provider Abstraction:** The generative AI features rely on an abstract LLM interface. While the current deployment uses a local Ollama service to meet the container constraint , integrating OpenAI or Anthropic requires zero changes to the core business logic—only a new adapter class.

## 2. Database Schema: User Preferences
**Requirement:** Design a schema to store user preferences to drive the recommendation engine.

**Design Choice:** A hybrid approach combining explicit and implicit preferences.
1. **Explicit Preferences (`user_preferences` table):** This table contains a `topic_tag` column linked via a Foreign Key to the `users` table. This allows users to declare their baseline interests.
2. **Implicit Preferences (Borrow History):** The `borrows` and `reviews` tables act as implicit feedback loops.

**Rationale:** Relying solely on explicit tags is rigid. By combining the `topic_tag` with the user's historical interaction data, the system creates a multi-dimensional profile, solving the "Cold Start" problem for new users while dynamically learning as they borrow more books.

## 3. Asynchronous LLM Generation
**Requirement:** Handle LLM summarization and review sentiment analysis asynchronously.

**Design Choice:** LLM inference is I/O bound and computationally expensive. Running it synchronously would block the API. 

* **Implementation:** FastAPI's native `BackgroundTasks` handle these workflows. 
* **Execution Flow:** When a user uploads a book or submits a review, the API instantly returns a success status with the data marked as "Pending". The text payload is handed off to a background worker thread. This thread orchestrates the prompt to the local LLM, parses the response, and commits the summary/sentiment back to the PostgreSQL database safely.
* **Production Path:** While `BackgroundTasks` is highly efficient for this containerized setup, the service layer is designed so task execution can easily be swapped to a distributed message broker (e.g., Celery + Redis) for multi-node scaling.

## 4. ML Recommendation Engine
**Requirement:** Implement a recommendation algorithm using user preferences.

**Design Choice:** Content-Based Filtering via NLP (Natural Language Processing).

* **Algorithm:** The system utilizes `scikit-learn` to perform TF-IDF (Term Frequency-Inverse Document Frequency) vectorization on the AI-generated book summaries.
* **Mechanism:** When a user requests recommendations, the system aggregates the summaries of books they have heavily interacted with (aligned with their `topic_tag`). It then calculates the Cosine Similarity between this user "profile vector" and the vectors of all unread books in the database.
* **Rationale:** Content-Based Filtering was chosen over Collaborative Filtering because library systems frequently ingest new files. By vectorizing the text itself, LuminaLib can accurately recommend a brand-new book the second the LLM finishes summarizing it, based purely on the semantic concepts inside the text.

## 5. Security & Authentication
**Requirement:** JWT-based stateless authentication.

**Design Choice:** The `users` table was built from scratch. The API issues short-lived JWTs (JSON Web Tokens) encoded with the user's ID, ensuring the REST API remains entirely stateless. Route dependencies validate the token signature on every protected endpoint.

## 6. Documented Assumptions
The following assumptions were made during architecture and development:

1. **Hardware Constraints & Model Selection:** The Docker Compose setup is configured to pull and run the `llama3` model via Ollama. This choice was made to ensure high-quality, nuanced text generation for book summaries and sentiment analysis. It is assumed the evaluation environment has sufficient resources (approx. 8GB+ RAM) to run this model locally.
2. **Storage:** Local volume mapping for book ingestion satisfies the "abstracted storage" requirement for this environment, prioritizing a seamless, one-command `docker-compose up` experience.
3. **Review Policy Constraints:** A strict database constraint assumes a user cannot review a book they do not have a registered `borrow` record for, ensuring sentiment analysis is driven by actual readers.
