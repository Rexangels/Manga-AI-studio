# manga/generation_service.py
class MangaGenerationService:
    def __init__(self, user, project=None):
        self.user = user
        self.project = project
        self.user_profile = UserProfile.objects.get(user=user)
        
    def can_generate(self):
        """Check if user has available quota"""
        return QuotaService.check_user_quota(self.user_profile)
    
    def generate_manga(self, narrative, panel_count=4, model_id=None, template_id=None):
        """Generate a complete manga page from narrative"""
        if not self.can_generate():
            raise QuotaExceeded("You've reached your monthly page limit")
        
        # Choose appropriate models based on subscription tier
        llm_provider, image_provider = self._get_providers(model_id)
        
        # 1. Create project if not provided
        if not self.project:
            self.project = MangaProject.objects.create(
                user=self.user,
                title=f"Project {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                narrative=narrative
            )
        
        # 2. Extract characters for consistency
        character_service = CharacterConsistencyService(self.project.id)
        characters = character_service.extract_characters(narrative)
        
        # 3. Use LLM to break down narrative into panel prompts
        llm_service = AIServiceRegistry.get('llm', llm_provider)
        panel_data = llm_service.parse_narrative(narrative, panel_count)
        
        # 4. Select template (if not specified)
        if not template_id:
            template = TemplateService.suggest_template(narrative, panel_count)
        else:
            template = Template.objects.get(id=template_id)
        
        self.project.template = template
        self.project.save()
        
        # 5. Generate images for each panel
        image_service = AIServiceRegistry.get('image', image_provider)
        panels = []
        
        for i, data in enumerate(panel_data, start=1):
            # Enhance prompt with character consistency
            enhanced_prompt, seed_info = character_service.inject_character_consistency(
                data['image_prompt']
            )
            
            # Determine image quality based on subscription
            quality_settings = self._get_quality_settings()
            
            # Generate image
            image_params = {
                **seed_info,
                **quality_settings
            }
            image_url = image_service.generate_image(enhanced_prompt, image_params)
            
            # Create panel
            panel = Panel.objects.create(
                project=self.project,
                panel_number=i,
                description=data['description'],
                prompt=data['image_prompt'],
                enhanced_prompt=enhanced_prompt,
                image_url=image_url
            )
            panels.append(panel)
        
        # 6. Apply template layout
        TemplateService.apply_template(panels, template)
        
        # 7. Track usage
        QuotaService.increment_usage(self.user_profile)
        
        return self.project
    
    def _get_providers(self, model_id=None):
        """Get appropriate AI providers based on subscription and model"""
        # Default providers by tier
        tier_providers = {
            'FREE': ('huggingface', 'stability-basic'),
            'BASIC': ('openai', 'stability-standard'),
            'PRO': ('openai', 'stability-creative'),
            'ENTERPRISE': ('anthropic', 'midjourney')
        }
        
        # If model ID is provided, look up specific provider settings
        if model_id:
            model = AIModel.objects.get(id=model_id)
            return model.llm_provider, model.image_provider
        
        # Otherwise use defaults for tier
        return tier_providers.get(
            self.user_profile.subscription_tier, 
            ('huggingface', 'stability-basic')
        )
    
    def _get_quality_settings(self):
        """Get image quality settings based on subscription tier"""
        quality_settings = {
            'FREE': {
                'width': 512,
                'height': 512,
                'steps': 30,
                'cfg_scale': 7
            },
            'BASIC': {
                'width': 768,
                'height': 768,
                'steps': 40,
                'cfg_scale': 7.5
            },
            'PRO': {
                'width': 1024,
                'height': 1024,
                'steps': 50,
                'cfg_scale': 8
            },
            'ENTERPRISE': {
                'width': 1536,
                'height': 1536,
                'steps': 60,
                'cfg_scale': 9
            }
        }
        
        return quality_settings.get(
            self.user_profile.subscription_tier, 
            quality_settings['FREE']
        )