import httpx
import traceback
from app.core.config import settings
import os
from dotenv import load_dotenv


load_dotenv()

class OllamaService:
    def __init__(self):
        # Grabs the URL from .env locally, or from docker-compose when contanerized
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # --- TOOL 1: SUMMARIZATION (For Books) ---
    async def generate_summary(self, text: str) -> str:
        prompt = f"Summarize this in 3 sentences: {text[:2000]}"
        
        # We keep the 600s timeout because your machine needs it
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": "tinyllama",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json().get("response", "No response key")
            except Exception as e:
                return f"Error: {repr(e)}"

    # --- TOOL 2: SENTIMENT ANALYSIS (For Reviews) ---
    async def analyze_sentiment(self, review_text: str) -> str:
        prompt = (
            f"Analyze the sentiment of the following book review. "
            f"Reply with ONLY one word: 'Positive', 'Negative', or 'Neutral'.\n\n"
            f"Review: {review_text}"
        )
        
        # Sentiment is faster, so 30-60 seconds is usually enough
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": "tinyllama",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                
                # Clean up the answer (remove extra spaces or punctuation)
                sentiment = response.json().get("response", "Unknown").strip()
                
                # Simple fallback if AI blabbers
                if "positive" in sentiment.lower(): return "Positive"
                if "negative" in sentiment.lower(): return "Negative"
                return "Neutral"
            except Exception as e:
                return f"Error: {repr(e)}"