# ai_services/providers/stable_diffusion_adapter.py
from ..image import ImageGenerationService
import requests
import json
import os
import base64
from django.conf import settings

class StableDiffusionService(ImageGenerationService):
    def configure(self, api_key=None, api_url=None, model="stable-diffusion-xl-1024-v1-0"):
        """
        Configure the Stable Diffusion service
        
        Args:
            api_key (str): API key for Stable Diffusion API
            api_url (str): URL endpoint for Stable Diffusion API
            model (str): Model to use for generation
        """
        self.api_key = api_key or settings.STABLE_DIFFUSION_API_KEY
        self.api_url = api_url or settings.STABLE_DIFFUSION_API_URL
        self.model = model
        
    def generate_image(self, prompt, parameters=None):
        """
        Generate an image using Stable Diffusion
        
        Args:
            prompt (str): The image generation prompt
            parameters (dict, optional): Additional parameters for customization
            
        Returns:
            str: URL to the generated image
        """
        # Default parameters
        default_params = {
            "width": 768,
            "height": 768,
            "steps": 30,
            "cfg_scale": 7.5,
            "seed": None,
            "sampler": "DPM++ 2M Karras"
        }
        
        # Update with user-provided parameters
        if parameters:
            default_params.update(parameters)
            
        payload = {
            "prompt": prompt,
            "negative_prompt": "low quality, bad anatomy, worst quality, low resolution",
            **default_params
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{self.api_url}/text2img", headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Error generating image: {response.text}")
            
        # Handle the response based on API format
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
        # Option 1: API returns a URL directly
        if 'url' in response:
            return response['url']
            
        # Option 2: API returns base64 encoded image
        if 'images' in response and len(response['images']) > 0:
            image_data = response['images'][0]
            if isinstance(image_data, str):
                # It's likely base64 encoded
                return self._save_base64_image(image_data)
        
        # Option 3: Different response format
        if 'output' in response and 'data' in response['output']:
            return self._save_base64_image(response['output']['data'])
            
        raise ValueError("Unexpected response format from Stable Diffusion API")
    
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