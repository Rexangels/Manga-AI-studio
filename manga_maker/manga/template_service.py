# manga/template_service.py
class TemplateService:
    @staticmethod
    def get_available_templates(user):
        """Get templates available for user based on subscription tier"""
        user_profile = UserProfile.objects.get(user=user)
        
        # Define template access by tier
        tier_template_access = {
            'FREE': ['basic-grid', 'simple-vertical'],
            'BASIC': ['basic-grid', 'simple-vertical', 'action-focused', 'dialogue-heavy'],
            'PRO': Template.objects.values_list('slug', flat=True),
            'ENTERPRISE': Template.objects.values_list('slug', flat=True)
        }
        
        template_slugs = tier_template_access.get(user_profile.subscription_tier, ['basic-grid'])
        
        if user_profile.subscription_tier == 'ENTERPRISE':
            # Include custom templates for enterprise users
            custom_template_slugs = Template.objects.filter(
                created_by=user
            ).values_list('slug', flat=True)
            template_slugs = list(template_slugs) + list(custom_template_slugs)
        
        return Template.objects.filter(slug__in=template_slugs)
    
    @staticmethod
    def suggest_template(narrative, panel_count):
        """Use LLM to suggest the best template based on narrative content"""
        llm_service = AIServiceRegistry.get('llm', 'openai')
        
        templates = Template.objects.all()
        template_descriptions = [
            f"{t.name}: {t.description}" for t in templates
        ]
        
        prompt = (
            "Based on the following narrative and panel count, suggest the best manga layout template. "
            f"Panel count: {panel_count}\n\n"
            f"Narrative: {narrative}\n\n"
            "Available templates:\n"
            f"{chr(10).join(template_descriptions)}\n\n"
            "Return only the template name that would best fit this narrative."
        )
        
        suggested_template_name = llm_service.execute(prompt)
        
        # Find the closest matching template
        try:
            return Template.objects.get(name__iexact=suggested_template_name.strip())
        except Template.DoesNotExist:
            # Fallback to closest match
            templates = Template.objects.all()
            closest_match = None
            highest_ratio = 0
            
            for template in templates:
                ratio = difflib.SequenceMatcher(None, template.name.lower(), 
                                               suggested_template_name.lower()).ratio()
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    closest_match = template
            
            # If we found a reasonable match (>60% similarity)
            if highest_ratio > 0.6:
                return closest_match
            
            # Ultimate fallback - basic grid template
            return Template.objects.get(slug='basic-grid')
    
    @staticmethod
    def apply_template(panels, template):
        """Apply template to arrange panels in the specified layout"""
        layout_data = json.loads(template.layout_json)
        
        # Ensure we have the right number of panel positions
        if len(panels) != len(layout_data['positions']):
            # Adapt layout for different panel counts
            layout_data = TemplateService._adapt_layout(layout_data, len(panels))
        
        # Apply layout positions to panels
        for i, panel in enumerate(panels):
            if i < len(layout_data['positions']):
                panel.position_x = layout_data['positions'][i]['x']
                panel.position_y = layout_data['positions'][i]['y']
                panel.width = layout_data['positions'][i]['width']
                panel.height = layout_data['positions'][i]['height']
            panel.save()
        
        return panels
    
    @staticmethod
    def _adapt_layout(layout_data, panel_count):
        """Adapt a layout to fit a different number of panels"""
        original_count = len(layout_data['positions'])
        
        if panel_count == original_count:
            return layout_data
        
        # For fewer panels, use subset of positions
        if panel_count < original_count:
            layout_data['positions'] = layout_data['positions'][:panel_count]
            return layout_data
        
        # For more panels, use an algorithm to split existing panels
        # This is a simplified approach; a more complex algorithm would be used in production
        new_positions = layout_data['positions'].copy()
        
        # Continue splitting the largest panel until we have enough
        while len(new_positions) < panel_count:
            # Find largest panel by area
            largest_panel_idx = 0
            largest_area = 0
            
            for i, pos in enumerate(new_positions):
                area = pos['width'] * pos['height']
                if area > largest_area:
                    largest_area = area
                    largest_panel_idx = i
            
            # Split the panel (horizontally if wider, vertically if taller)
            panel = new_positions[largest_panel_idx]
            if panel['width'] >= panel['height']:
                # Split horizontally
                new_positions[largest_panel_idx]['width'] = panel['width'] / 2
                new_positions.append({
                    'x': panel['x'] + panel['width'],
                    'y': panel['y'],
                    'width': panel['width'],
                    'height': panel['height']
                })
            else:
                # Split vertically
                new_positions[largest_panel_idx]['height'] = panel['height'] / 2
                new_positions.append({
                    'x': panel['x'],
                    'y': panel['y'] + panel['height'],
                    'width': panel['width'],
                    'height': panel['height']
                })
        
        layout_data['positions'] = new_positions
        return layout_data