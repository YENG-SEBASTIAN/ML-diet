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

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Calculate BMI if weight and height are provided
        if self.weight and self.height:
            self.bmi = round(self.weight / (self.height ** 2), 1)
        super().save(*args, **kwargs)
