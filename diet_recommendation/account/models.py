from django.contrib.auth.models import User, AbstractUser
from django.db import models


class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    HEALTH_GOAL_CHOICES = [
        ('gain weight', 'Gain Weight'),
        ('lose weight', 'Lose Weight'),
        ('maintain weight', 'Maintain Weight'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bmi = models.FloatField(null=True, blank=True)
    health_goal = models.CharField(
        max_length=50,
        choices=HEALTH_GOAL_CHOICES
    )
    weight = models.FloatField(null=True, blank=True)  # Weight in kilograms
    height = models.FloatField(null=True, blank=True)  # Height in meters
    target_weight = models.FloatField(null=True, blank=True)  # Target weight in kilograms
    health_condition = models.TextField(null=True, blank=True)  # Health conditions, separated by commas
    allergies = models.TextField(null=True, blank=True)  # Allergies, separated by commas

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Convert weight and height to float if they are not None
        try:
            if self.weight and self.height:
                self.weight = float(self.weight)
                self.height = float(self.height)
                self.bmi = round(self.weight / (self.height ** 2), 1)
        except (ValueError, TypeError):
            # Handle the case where conversion fails (e.g., non-numeric values)
            self.bmi = None
        super().save(*args, **kwargs)
