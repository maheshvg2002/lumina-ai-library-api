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
        prompt = f"""You are an expert library assistant system. 
                 Your task is to provide a concise, engaging summary of the provided book text.

                 STRICT CONSTRAINTS:
                 1. You MUST respond in English.
                 2. The summary must be exactly 3 sentences long.
                 3. Do not include any conversational filler (e.g., "Here is the summary:").

                 Book Text:
                 {text[:2000]}
                 """
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return response.json().get("response", "No response key").strip()
            except Exception as e:
                return f"Error: {repr(e)}"

    # --- TOOL 2: SENTIMENT ANALYSIS (For Reviews) ---
    async def analyze_sentiment(self, review_text: str) -> str:
        prompt = f"""You are an automated sentiment analysis pipeline.
                 Classify the sentiment of the following book review.

                 STRICT CONSTRAINTS:
                 - Reply with ONLY ONE WORD from this list: [Positive, Negative, Neutral].
                 - Do not add punctuation.
                 - Do not explain your reasoning.

                 Review: {review_text}
                """
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False},
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