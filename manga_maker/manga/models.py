from django.db import models
from django.contrib.auth.models import User
import datetime
import json
import uuid

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('BASIC', 'Basic'),
            ('PRO', 'Pro'),
            ('ENTERPRISE', 'Enterprise')
        ],
        default='FREE'
    )
    pages_created = models.IntegerField(default=0)
    pages_quota = models.IntegerField(default=5)  # Default for free tier
    quota_reset_date = models.DateField(default=datetime.date.today)
    
    @property
    def remaining_pages(self):
        return max(0, self.pages_quota - self.pages_created)
    
    def __str__(self):
        return f"{self.user.username}'s Profile ({self.subscription_tier})"


class Template(models.Model):
    """Manga page layout template"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    layout_json = models.TextField()  # JSON representation of layout
    preview_image = models.ImageField(upload_to='templates/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    min_panels = models.IntegerField(default=1)
    max_panels = models.IntegerField(default=12)
    
    def __str__(self):
        return self.name
    
    @property
    def layout(self):
        """Return the layout as a Python object"""
        return json.loads(self.layout_json)


class AIModel(models.Model):
    """AI model configuration"""
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    llm_provider = models.CharField(max_length=50)
    image_provider = models.CharField(max_length=50)
    tier_required = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('BASIC', 'Basic'),
            ('PRO', 'Pro'),
            ('ENTERPRISE', 'Enterprise')
        ],
        default='FREE'
    )
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)  # Provider-specific settings
    
    def __str__(self):
        return f"{self.name} ({self.tier_required})"


class MangaProject(models.Model):
    """A manga project, containing a set of panels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    narrative = models.TextField()
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)