"""
LLM Service using Google Gemini API
"""
import os
from google import genai


class LLMService:
    def __init__(
        self,
        gemini_api_key: str,
        gemini_model: str = "gemini-2.5-flash",
        max_context_length: int = 2000,
    ) -> None:
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.max_context_length = max_context_length
        
        # Set API key in environment for the SDK
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        
        # Initialize the Gemini client
        self.client = genai.Client()

    def generate_text(self, prompt: str) -> str:
        """Generate text using Google Gemini API"""
        return self._generate_gemini(prompt)

    def _generate_gemini(self, prompt: str) -> str:
        """Generate text using Google Gemini API via official SDK"""
        if not self.gemini_api_key:
            return "Error: Gemini API key is not configured."

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "Unable to generate an answer."
                
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return f"Error generating answer: {e}"
