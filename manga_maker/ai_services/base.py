# ai_services/base.py
from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    def configure(self, **kwargs):
        pass
    
    @abstractmethod
    def execute(self, input_data):
        pass

# ai_services/llm.py
class LLMService(AIService):
    @abstractmethod
    def parse_narrative(self, text, panel_count=4):
        pass

# ai_services/image.py
class ImageGenerationService(AIService):
    @abstractmethod
    def generate_image(self, prompt, parameters=None):
        pass