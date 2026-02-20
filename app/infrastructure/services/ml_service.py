from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class RecommendationEngine:
    def __init__(self):
        # TF-IDF turns text (book summaries) into mathematical vectors
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def get_content_based_recommendations(
        self, 
        user_liked_summaries: List[str], 
        all_other_books: List[dict] # dict containing id, title, summary
    ) -> List[dict]:
        
        # If the user hasn't read anything, or books have no summaries, we can't run the ML
        if not user_liked_summaries or not all_other_books:
            return []

        # Combine the user's liked text into one giant "Profile" string
        user_profile_text = " ".join(user_liked_summaries)

        # Prepare the data for the ML model
        book_ids = []
        documents = [user_profile_text] # Index 0 is the User Profile
        
        for book in all_other_books:
            # Only include books that actually have an AI summary
            if book["summary"] and book["summary"] != "Pending...":
                book_ids.append(book["id"])
                documents.append(book["summary"])

        if len(documents) <= 1:
            return [] # No valid books to compare against

        # 1. Transform text into ML vectors
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # 2. Calculate Cosine Similarity between the User Profile (index 0) and all Books
        # This tells us mathematically how similar the text is (0.0 to 1.0)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # 3. Attach scores to books and sort them
        scored_books = []
        for idx, score in enumerate(cosine_sim):
            scored_books.append({
                "book_id": book_ids[idx],
                "ml_score": float(score)
            })

        # Sort by highest score first
        scored_books.sort(key=lambda x: x["ml_score"], reverse=True)
        
        return scored_books