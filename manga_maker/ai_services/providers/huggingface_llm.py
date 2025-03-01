# ai_services/providers/huggingface_llm.py
from ..llm import LLMService
import requests

class HuggingFaceLLMService(LLMService):
    def configure(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        
    def parse_narrative(self, text, panel_count=4):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        prompt = f"Split this narrative into {panel_count} manga panels...\n\n{text}"
        response = requests.post(self.api_url, headers=headers, json={"inputs": prompt})
        return self._parse_response(response.json())