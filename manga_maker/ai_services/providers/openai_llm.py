# ai_services/providers/openai_llm.py
from ..llm import LLMService
import openai
import json

class OpenAILLMService(LLMService):
    def configure(self, api_key, model="gpt-4"):
        """
        Configure the OpenAI LLM service
        
        Args:
            api_key (str): OpenAI API key
            model (str): Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
    def parse_narrative(self, text, panel_count=4):
        """
        Parse a narrative into manga panels using OpenAI
        
        Args:
            text (str): Narrative text to parse
            panel_count (int): Number of panels to divide into
            
        Returns:
            list: List of panel data dictionaries
        """
        system_prompt = """
        You are a manga panel designer. Break down the given narrative into specified number of manga panels.
        For each panel, provide:
        1. A clear description of what happens in the panel
        2. An image generation prompt that will create a high-quality manga style illustration
        
        Format your response as a JSON array of objects, where each object has:
        - "description": detailed description of panel content
        - "image_prompt": prompt optimized for manga-style image generation
        
        Be specific in image prompts, including character positions, emotions, backgrounds, and any manga-specific elements.
        """
        
        prompt = f"Split this narrative into {panel_count} manga panels:\n\n{text}"
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return self._parse_response(response)
        except Exception as e:
            # Use the generic text-based fallback if JSON parsing fails
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a manga panel designer."},
                    {"role": "user", "content": f"Split this narrative into {panel_count} manga panels, numbered 1-{panel_count}:\n\n{text}"}
                ]
            )
            return self._parse_response(response)
    
    def _parse_response(self, response):
        """
        Parse OpenAI response into structured panel data
        
        Args:
            response: OpenAI API response
            
        Returns:
            list: List of panel data dictionaries
        """
        # Extract the content from OpenAI response
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content
        else:
            content = str(response)
            
        # Try to parse as JSON
        try:
            data = json.loads(content)
            if "panels" in data:
                return data["panels"]
            elif isinstance(data, list):
                return data
            else:
                # If it's an object but not in expected format, make a best guess
                return [{"description": str(item), "image_prompt": str(item)} 
                        for item in data.values() if isinstance(item, str)]
        except json.JSONDecodeError:
            # Fallback to text parsing
            return super()._parse_text_response(content)
            
    def execute(self, input_data):
        """
        Execute a general LLM prompt using OpenAI
        
        Args:
            input_data (str): Prompt to send to the LLM
            
        Returns:
            str: Response from the LLM
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": input_data}
            ]
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            return response.choices[0].message.content
        
        return str(response)