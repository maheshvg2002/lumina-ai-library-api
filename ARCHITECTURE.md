# Architecture & Design Decisions: LuminaLib

This document outlines the architectural patterns, data models, and system design choices made for the LuminaLib platform. [cite_start]The system was designed with a focus on Clean Architecture, SOLID principles, and horizontal extensibility[cite: 7, 30].

## 1. Clean Architecture & Interface-Driven Development
[cite_start]The application is structured in layers to decouple the business logic from the external frameworks (FastAPI), infrastructure (PostgreSQL), and third-party services (LLMs, Storage)[cite: 30].

### Dependency Injection (DI)
[cite_start]FastAPI's dependency injection system is utilized globally[cite: 30]. Database sessions, configuration settings, and external service clients are injected into the route handlers. This ensures that the application is easily testable and decoupled.

### Swappable Interfaces (The "Plugin" Architecture)
[cite_start]The architecture supports swapping components with minimal friction[cite: 31]. This is achieved using Python `Protocols` / Abstract Base Classes:

* **Storage Abstraction:** File ingestion does not hardcode local file paths into the business logic. [cite_start]Instead, a `StorageBackend` interface is defined[cite: 17]. [cite_start]Currently, it uses local storage, but switching to AWS S3 or MinIO simply requires writing a new class that implements the interface and updating the configuration[cite: 17, 32].
* **LLM Provider Abstraction:** The generative AI features rely on an abstract LLM interface. [cite_start]While the current deployment uses a local Ollama service to meet the container constraint [cite: 45][cite_start], integrating OpenAI or Anthropic requires zero changes to the core business logic—only a new adapter class[cite: 33].

## 2. Database Schema: User Preferences
[cite_start]**Requirement:** Design a schema to store user preferences to drive the recommendation engine[cite: 26].

[cite_start]**Design Choice:** A hybrid approach combining explicit and implicit preferences[cite: 27].
1. **Explicit Preferences (`user_preferences` table):** This table contains a `topic_tag` column linked via a Foreign Key to the `users` table. This allows users to declare their baseline interests.
2. **Implicit Preferences (Borrow History):** The `borrows` and `reviews` tables act as implicit feedback loops.

**Rationale:** Relying solely on explicit tags is rigid. By combining the `topic_tag` with the user's historical interaction data, the system creates a multi-dimensional profile, solving the "Cold Start" problem for new users while dynamically learning as they borrow more books.

## 3. Asynchronous LLM Generation
[cite_start]**Requirement:** Handle LLM summarization and review sentiment analysis asynchronously[cite: 23, 24].

**Design Choice:** LLM inference is I/O bound and computationally expensive. Running it synchronously would block the API. 

* [cite_start]**Implementation:** FastAPI's native `BackgroundTasks` handle these workflows[cite: 56]. 
* [cite_start]**Execution Flow:** When a user uploads a book or submits a review, the API instantly returns a success status with the data marked as "Pending"[cite: 23, 24]. The text payload is handed off to a background worker thread. This thread orchestrates the prompt to the local LLM, parses the response, and commits the summary/sentiment back to the PostgreSQL database safely.
* **Production Path:** While `BackgroundTasks` is highly efficient for this containerized setup, the service layer is designed so task execution can easily be swapped to a distributed message broker (e.g., Celery + Redis) for multi-node scaling.

## 4. ML Recommendation Engine
[cite_start]**Requirement:** Implement a recommendation algorithm using user preferences[cite: 28].

[cite_start]**Design Choice:** Content-Based Filtering via NLP (Natural Language Processing)[cite: 28, 57].

* **Algorithm:** The system utilizes `scikit-learn` to perform TF-IDF (Term Frequency-Inverse Document Frequency) vectorization on the AI-generated book summaries.
* **Mechanism:** When a user requests recommendations, the system aggregates the summaries of books they have heavily interacted with (aligned with their `topic_tag`). It then calculates the Cosine Similarity between this user "profile vector" and the vectors of all unread books in the database.
* **Rationale:** Content-Based Filtering was chosen over Collaborative Filtering because library systems frequently ingest new files. By vectorizing the text itself, LuminaLib can accurately recommend a brand-new book the second the LLM finishes summarizing it, based purely on the semantic concepts inside the text.

## 5. Security & Authentication
[cite_start]**Requirement:** JWT-based stateless authentication[cite: 10].

[cite_start]**Design Choice:** The `users` table was built from scratch[cite: 12]. [cite_start]The API issues short-lived JWTs (JSON Web Tokens) encoded with the user's ID, ensuring the REST API remains entirely stateless[cite: 10]. Route dependencies validate the token signature on every protected endpoint.

## 6. Documented Assumptions
The following assumptions were made during architecture and development:

1. [cite_start]**Hardware Constraints:** Assuming the system will be evaluated on standard hardware without a dedicated high-end GPU, the Docker Compose file is configured to pull an efficient, quantized model (`tinyllama`)[cite: 45]. 
2. [cite_start]**Storage:** Local volume mapping for book ingestion satisfies the "abstracted storage" requirement for this environment, prioritizing a seamless, one-command `docker-compose up` experience[cite: 17, 42].
3. [cite_start]**Review Policy Constraints:** A strict database constraint assumes a user cannot review a book they do not have a registered `borrow` record for, ensuring sentiment analysis is driven by actual readers[cite: 21].
