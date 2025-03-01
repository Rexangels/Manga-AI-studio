# character_service.py
class CharacterConsistencyService:
    def __init__(self, project_id):
        self.project_id = project_id
        self.characters = {}
        self._load_characters()
    
    def _load_characters(self):
        """Load character profiles from database"""
        characters = CharacterProfile.objects.filter(project_id=self.project_id)
        for character in characters:
            self.characters[character.name] = {
                'description': character.description,
                'seed': character.seed,
                'visual_traits': character.visual_traits,
                'style_reference': character.style_reference
            }
    
    def extract_characters(self, narrative):
        """Use LLM to extract character information from narrative"""
        llm_service = AIServiceRegistry.get('llm', 'openai')
        
        prompt = (
            "Extract character names and descriptions from this narrative. "
            "For each character, identify visual traits such as hair color, "
            "eye color, clothing, and distinguishing features.\n\n"
            f"Narrative: {narrative}\n\n"
            "Return as a JSON array of character objects with 'name' and 'visual_traits' keys."
        )
        
        result = llm_service.execute(prompt)
        return self._process_character_data(result)
    
    def _process_character_data(self, character_data):
        """Process and store character data extracted by LLM"""
        for character in character_data:
            # If we already have this character, update/merge info
            if character['name'] in self.characters:
                # Update with new information while preserving the seed
                self.characters[character['name']]['visual_traits'] = character['visual_traits']
            else:
                # Create new character profile
                self.characters[character['name']] = {
                    'description': character.get('description', ''),
                    'visual_traits': character.get('visual_traits', ''),
                    'seed': random.randint(1, 1000000),  # Generate consistent seed
                    'style_reference': None
                }
                
                # Save to database
                CharacterProfile.objects.create(
                    project_id=self.project_id,
                    name=character['name'],
                    description=character.get('description', ''),
                    visual_traits=character.get('visual_traits', ''),
                    seed=self.characters[character['name']]['seed']
                )
        
        return self.characters
    
    def inject_character_consistency(self, prompt, character_names=None):
        """Enhance image generation prompt with character consistency info"""
        if not character_names:
            # Extract character names mentioned in the prompt
            character_names = [name for name in self.characters.keys() 
                              if name.lower() in prompt.lower()]
        
        character_descriptions = []
        for name in character_names:
            if name in self.characters:
                char = self.characters[name]
                desc = f"{name}: {char['visual_traits']}"
                character_descriptions.append(desc)
        
        if character_descriptions:
            consistency_prompt = (
                "\nEnsure character consistency: "
                f"{'; '.join(character_descriptions)}"
            )
            enhanced_prompt = f"{prompt}{consistency_prompt}"
            
            # Add seed info for the image generation API if applicable
            seed_info = {}
            if character_names and character_names[0] in self.characters:
                # Use the seed of the main character for consistency
                seed_info['seed'] = self.characters[character_names[0]]['seed']
                
            return enhanced_prompt, seed_info
        
        return prompt, {}