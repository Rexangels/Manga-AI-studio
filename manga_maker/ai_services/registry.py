# ai_services/registry.py
class AIServiceRegistry:
    _instances = {}
    
    @classmethod
    def register(cls, service_type, provider, instance):
        key = (service_type, provider)
        cls._instances[key] = instance
        
    @classmethod
    def get(cls, service_type, provider):
        key = (service_type, provider)
        if key not in cls._instances:
            raise KeyError(f"No service registered for {service_type} with provider {provider}")
        return cls._instances[key]