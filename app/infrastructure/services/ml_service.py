from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:
    """
    Engine to generate book recommendations using TF-IDF vectorization
    and Cosine Similarity.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def get_content_based_recommendations(
        self,
        user_liked_summaries: List[str],
        all_other_books: List[dict],  # dict containing id, title, summary
    ) -> List[dict]:
        """
        Calculates similarity scores between a user profile and available books.
        """

        if not user_liked_summaries or not all_other_books:
            return []

        # Construct User Profile by merging liked content
        user_profile_text = " ".join(user_liked_summaries)

        book_ids = []
        documents = [user_profile_text]  # Index 0 is the User Profile

        for book in all_other_books:
            if book["summary"] and book["summary"] != "Pending...":
                book_ids.append(book["id"])
                documents.append(book["summary"])

        if len(documents) <= 1:
            return []

        # 1. Vectorization: Convert text documents into numerical feature vectors
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # 2. Similarity Calculation: Measure the angle between vectors
        # (Score 1.0 means identical content, 0.0 means completely different)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # 3. Ranking: Map scores back to IDs and sort by relevance
        scored_books = []
        for idx, score in enumerate(cosine_sim):
            scored_books.append({"book_id": book_ids[idx], "ml_score": float(score)})

        # Sort by highest score first
        scored_books.sort(key=lambda x: x["ml_score"], reverse=True)

        return scored_books
