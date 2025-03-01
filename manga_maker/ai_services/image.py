# ai_services/image.py
from .base import AIService
from abc import abstractmethod

class ImageGenerationService(AIService):
    @abstractmethod
    def generate_image(self, prompt, parameters=None):
        """
        Generate an image from the given prompt
        
        Args:
            prompt (str): Prompt describing the desired image
            parameters (dict, optional): Additional parameters for the image generation
                Commonly used parameters include:
                - width: Image width in pixels
                - height: Image height in pixels
                - cfg_scale: How closely the image follows the prompt
                - steps: Number of sampling steps (more = higher quality)
                - seed: Random seed for consistent results
                
        Returns:
            str: URL or path to the generated image
        """
        pass
    
    def execute(self, input_data):
        """
        Implementation of the general execute method for image generation
        
        Args:
            input_data (dict): Dictionary with 'prompt' and optional 'parameters' keys
            
        Returns:
            str: URL or path to the generated image
        """
        if isinstance(input_data, str):
            # If input is just a string, treat it as the prompt
            return self.generate_image(input_data)
        
        prompt = input_data.get('prompt')
        parameters = input_data.get('parameters', {})
        
        if not prompt:
            raise ValueError("Input must contain a 'prompt' field")
            
        return self.generate_image(prompt, parameters)