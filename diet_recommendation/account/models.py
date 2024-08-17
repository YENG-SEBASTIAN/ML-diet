from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bmi = models.FloatField(null=True, blank=True)
    health_goal = models.CharField(max_length=50, choices=[('gain weight', 'Gain Weight'), ('lose weight', 'Lose Weight'), ('maintain weight', 'Maintain Weight')])

    def __str__(self):
        return f'{self.user.username} Profile'
