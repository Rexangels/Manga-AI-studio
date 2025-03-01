# ai_services/providers/openai_llm.py
from ..llm import LLMService
import openai

class OpenAILLMService(LLMService):
    def configure(self, api_key, model="gpt-4"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
    def parse_narrative(self, text, panel_count=4):
        prompt = f"Split this narrative into {panel_count} manga panels..."
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a manga panel designer."},
                {"role": "user", "content": prompt + text}
            ]
        )
        return self._parse_response(response)