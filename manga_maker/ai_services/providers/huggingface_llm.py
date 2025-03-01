# ai_services/providers/huggingface_llm.py
from ..llm import LLMService
import requests
import json

class HuggingFaceLLMService(LLMService):
    def configure(self, api_key, model_name):
        """
        Configure the Hugging Face LLM service
        
        Args:
            api_key (str): Hugging Face API key
            model_name (str): Name of the model to use (e.g., "gpt2", "EleutherAI/gpt-neo-2.7B")
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
    def parse_narrative(self, text, panel_count=4):
        """
        Parse a narrative into manga panels using Hugging Face model
        
        Args:
            text (str): Narrative text to parse
            panel_count (int): Number of panels to divide into
            
        Returns:
            list: List of panel data dictionaries
        """
        prompt = f"""
        Split this narrative into {panel_count} manga panels. For each panel, provide a description and an image prompt.
        
        Narrative:
        {text}
        
        Format each panel as:
        Panel 1: [Panel description]
        Image prompt: [Detailed image generation prompt for manga style illustration]
        
        Panel 2: [Panel description]
        Image prompt: [Detailed image generation prompt for manga style illustration]
        
        ... and so on.
        """
        
        response = requests.post(
            self.api_url, 
            headers=self.headers, 
            json={"inputs": prompt, "parameters": {"max_length": 1000}}
        )
        
        if response.status_code != 200:
            raise Exception(f"Error from Hugging Face API: {response.text}")
            
        return self._parse_response(response.json())
    
    def _parse_response(self, response):
        """
        Parse Hugging Face API response into structured panel data
        
        Args:
            response: Hugging Face API response
            
        Returns:
            list: List of panel data dictionaries
        """
        # Handle different response formats from Hugging Face
        if isinstance(response, list) and len(response) > 0:
            if 'generated_text' in response[0]:
                text = response[0]['generated_text']
            else:
                text = str(response[0])
        elif isinstance(response, dict) and 'generated_text' in response:
            text = response['generated_text']
        else:
            text = str(response)
            
        # Parse the text to extract panels
        import re
        
        # Extract panels with descriptions and image prompts
        pattern = r"Panel (\d+):(.*?)(?:Image prompt:(.*?))?(?=Panel \d+:|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        
        panel_data = []
        
        if matches:
            for match in matches:
                panel_num, description, image_prompt = match
                description = description.strip()
                image_prompt = image_prompt.strip() if image_prompt else f"Manga panel of {description}"
                
                panel_data.append({
                    "description": description,
                    "image_prompt": image_prompt
                })
        else:
            # Fallback to simpler parsing
            return super()._parse_text_response(text)
        
        return panel_data
    
    def execute(self, input_data):
        """
        Execute a general LLM prompt using Hugging Face
        
        Args:
            input_data (str): Prompt to send to the LLM
            
        Returns:
            str: Response from the LLM
        """
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": input_data}
        )
        
        if response.status_code != 200:
            raise Exception(f"Error from Hugging Face API: {response.text}")
            
        result = response.json()
        
        # Extract text from different response formats
        if isinstance(result, list) and len(result) > 0:
            if 'generated_text' in result[0]:
                return result[0]['generated_text']
            return str(result[0])
        elif isinstance(result, dict) and 'generated_text' in result:
            return result['generated_text']
            
        return str(result)