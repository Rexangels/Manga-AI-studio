# ai_services/llm.py
from .base import AIService
from abc import abstractmethod

class LLMService(AIService):
    @abstractmethod
    def parse_narrative(self, text, panel_count=4):
        """
        Parse a narrative text and divide it into manga panels
        
        Args:
            text (str): The narrative text to parse
            panel_count (int): Number of panels to divide the narrative into
            
        Returns:
            list: A list of panel data dictionaries containing panel details
        """
        pass
    
    def execute(self, input_data):
        """
        Execute a generic LLM prompt
        
        Args:
            input_data (str): The prompt to send to the LLM
            
        Returns:
            Any: The response from the LLM
        """
        raise NotImplementedError("Each LLM service must implement this method")
    
    def _parse_response(self, response):
        """
        Parse the raw LLM response into structured panel data
        
        Args:
            response (dict): Raw response from the LLM API
            
        Returns:
            list: A list of panel data dictionaries
        """
        # Default implementation for simple text responses
        if isinstance(response, str):
            return self._parse_text_response(response)
        
        # Handle OpenAI-style responses
        if isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._parse_text_response(content)
        
        # Handle Hugging Face-style responses
        if isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict):
            if 'generated_text' in response[0]:
                return self._parse_text_response(response[0]['generated_text'])
        
        # Generic fallback
        return [{"description": "Failed to parse response", "image_prompt": "A blank manga panel"}]
    
    def _parse_text_response(self, text):
        """
        Parse text response into panel data
        
        Args:
            text (str): Text response from LLM
            
        Returns:
            list: List of panel data dictionaries
        """
        import re
        
        # Simple parsing for panel format: Panel 1: description
        panel_pattern = r"Panel (\d+)[:|-]\s*(.*?)(?=Panel \d+|$)"
        panels = re.findall(panel_pattern, text, re.DOTALL)
        
        if not panels:
            # Alternative format: 1. description
            panel_pattern = r"(\d+)[\.|\)]\s*(.*?)(?=\d+[\.|\)]|$)"
            panels = re.findall(panel_pattern, text, re.DOTALL)
        
        if not panels:
            # Fall back to simple text split
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            return [{"description": line, "image_prompt": line} for line in lines[:4]]
        
        panel_data = []
        for num, description in panels:
            description = description.strip()
            # Generate an image prompt based on the description
            image_prompt = f"Manga panel of {description}"
            panel_data.append({
                "description": description,
                "image_prompt": image_prompt
            })
        
        return panel_data