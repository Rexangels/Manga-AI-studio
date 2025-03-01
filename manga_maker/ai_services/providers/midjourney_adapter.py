# ai_services/providers/midjourney_adapter.py
from ..image import ImageGenerationService
import requests
import json
import time
from django.conf import settings

class MidjourneyService(ImageGenerationService):
    def configure(self, api_key=None, api_url=None):
        """
        Configure the Midjourney service
        
        Args:
            api_key (str): API key for Midjourney API
            api_url (str): URL endpoint for Midjourney API
        """
        self.api_key = api_key or settings.MIDJOURNEY_API_KEY
        self.api_url = api_url or "https://api.midjourney.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt, parameters=None):
        """
        Generate an image using Midjourney
        
        Args:
            prompt (str): The image generation prompt
            parameters (dict, optional): Additional parameters for customization
            
        Returns:
            str: URL to the generated image
        """
        # Default parameters
        default_params = {
            "width": 1024,
            "height": 1024,
            "style": "manga",  # Manga style by default
            "quality": "standard",
            "wait_for_completion": True,
            "timeout": 120  # Maximum wait time in seconds
        }
        
        # Update with user-provided parameters
        if parameters:
            default_params.update(parameters)
            
        # Extract wait parameters
        wait_for_completion = default_params.pop("wait_for_completion", True)
        timeout = default_params.pop("timeout", 120)
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "style": default_params.pop("style", "manga"),
            "dimensions": f"{default_params.pop('width', 1024)}x{default_params.pop('height', 1024)}",
            "quality": default_params.pop("quality", "standard"),
            **default_params
        }
        
        # Start the image generation job
        response = requests.post(
            f"{self.api_url}/imagine", 
            headers=self.headers, 
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Error starting image generation: {response.text}")
            
        job_data = response.json()
        job_id = job_data.get("job_id")
        
        if not job_id:
            raise Exception("No job ID returned from Midjourney API")
            
        # If not waiting for completion, return job ID
        if not wait_for_completion:
            return {"job_id": job_id, "status": "processing"}
            
        # Wait for job completion
        return self._wait_for_completion(job_id, timeout)
    
    def _wait_for_completion(self, job_id, timeout=120):
        """
        Wait for a Midjourney job to complete
        
        Args:
            job_id (str): The job ID to check
            timeout (int): Maximum wait time in seconds
            
        Returns:
            str: URL to the generated image
        """
        start_time = time.time()
        poll_interval = 5  # seconds
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.api_url}/job/{job_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Error checking job status: {response.text}")
                
            job_data = response.json()
            status = job_data.get("status")
            
            if status == "completed":
                # Job completed, return image URL
                image_url = job_data.get("image_url")
                if not image_url:
                    raise Exception("Job completed but no image URL returned")
                return image_url
                
            if status == "failed":
                raise Exception(f"Image generation failed: {job_data.get('error', 'Unknown error')}")
                
            # Wait before polling again
            time.sleep(poll_interval)
            
        raise Exception(f"Image generation timed out after {timeout} seconds")
    
    def check_job_status(self, job_id):
        """
        Check the status of a Midjourney job
        
        Args:
            job_id (str): The job ID to check
            
        Returns:
            dict: Job status data
        """
        response = requests.get(
            f"{self.api_url}/job/{job_id}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error checking job status: {response.text}")
            
        return response.json()