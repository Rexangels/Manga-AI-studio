from django.db import models

# Create your models here.
# manga/models.py
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
    quota_reset_date = models.DateField()
    
    @property
    def remaining_pages(self):
        return max(0, self.pages_quota - self.pages_created)

# Services to manage usage tracking
class QuotaService:
    @staticmethod
    def check_user_quota(user_profile):
        # Reset quota if we're past the reset date
        today = datetime.date.today()
        if today > user_profile.quota_reset_date:
            user_profile.pages_created = 0
            user_profile.quota_reset_date = today + datetime.timedelta(days=30)
            user_profile.save()
            
        # Check if user has remaining quota
        return user_profile.remaining_pages > 0
    
    @staticmethod
    def increment_usage(user_profile):
        user_profile.pages_created += 1
        user_profile.save()