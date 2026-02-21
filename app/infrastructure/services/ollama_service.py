import os

import httpx
from dotenv import load_dotenv

from app.core.interfaces import LLMProvider

load_dotenv()


class OllamaService(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- TOOL 1: SUMMARIZATION (For Books) ---
    async def generate_summary(self, text: str) -> str:
        prompt = f"Summarize this in 3 sentences: {text[:2000]}"

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": "tinyllama", "prompt": prompt, "stream": False},
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

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": "tinyllama", "prompt": prompt, "stream": False},
                )
                response.raise_for_status()

                sentiment = response.json().get("response", "Unknown").strip()

                if "positive" in sentiment.lower():
                    return "Positive"
                if "negative" in sentiment.lower():
                    return "Negative"
                return "Neutral"
            except Exception as e:
                return f"Error: {repr(e)}"
