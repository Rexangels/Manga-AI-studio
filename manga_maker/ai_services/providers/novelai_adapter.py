# ai_services/providers/novelai_adapter.py
from ..image import ImageGenerationService
import requests
import json
import base64
from django.conf import settings

class NovelAIService(ImageGenerationService):
    def configure(self, api_key=None, api_url=None):
        """
        Configure the NovelAI service
        
        Args:
            api_key (str): API key for NovelAI API
            api_url (str): URL endpoint for NovelAI API
        """
        self.api_key = api_key or settings.NOVELAI_API_KEY
        self.api_url = api_url or "https://api.novelai.net"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt, parameters=None):
        """
        Generate an image using NovelAI
        
        Args:
            prompt (str): The image generation prompt
            parameters (dict, optional): Additional parameters for customization
            
        Returns:
            str: URL to the generated image
        """
        # Default parameters - NovelAI specific
        default_params = {
            "width": 832,
            "height": 1216,
            "steps": 28,
            "scale": 11,
            "sampler": "k_euler_ancestral",
            "model": "nai-diffusion-3",
            "negative_prompt": "low quality, bad anatomy, worst quality"
        }
        
        # Update with user-provided parameters
        if parameters:
            # Map common parameter names to NovelAI specific ones
            if "cfg_scale" in parameters:
                parameters["scale"] = parameters.pop("cfg_scale")
                
            default_params.update(parameters)
            
        # Prepare request payload
        payload = {
            "input": prompt,
            "model": default_params.pop("model", "nai-diffusion-3"),
            "parameters": default_params
        }
        
        # Make API request
        response = requests.post(
            f"{self.api_url}/ai/generate-image",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Error generating image: {response.text}")
            
        # NovelAI typically returns a base64 encoded image
        response_data = response.json()
        
        # Save image and return URL
        return self._process_image_response(response_data)
    
    def _process_image_response(self, response):
        """
        Process the API response to store image and return URL
        
        Args:
            response (dict): API response data
            
        Returns:
            str: URL to access the saved image
        """
        # Extract base64 image data
        if 'image' in response:
            image_data = response['image']
            return self._save_base64_image(image_data)
            
        # Alternative response format
        if 'data' in response:
            return self._save_base64_image(response['data'])
            
        raise ValueError("Unexpected response format from NovelAI API")
    
    def _save_base64_image(self, base64_string):
        """
        Save base64 encoded image and return URL
        
        Args:
            base64_string (str): Base64 encoded image data
            
        Returns:
            str: URL to access the saved image
        """
        import uuid
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Remove potential metadata from base64 string
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
            
        # Decode base64 to binary
        image_data = base64.b64decode(base64_string)
        
        # Generate a unique filename
        filename = f"manga_panels/{uuid.uuid4()}.png"
        
        # Save file using Django's storage
        path = default_storage.save(filename, ContentFile(image_data))
        
        # Return the URL
        return default_storage.url(path)