from django.db import models
from account.models import User


class DietPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return self.name

class UserHealthHistroy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)  # Weight in kilograms
    height = models.FloatField(null=True, blank=True)  # Height in meters
    bmi = models.FloatField(null=True, blank=True)
    health_goal = models.CharField( max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Health histroy for {self.user.username}"
    
class DietRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=50)
    recommended_diet = models.TextField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    vitamins = models.TextField()
    minerals = models.TextField()
    health_benefits = models.TextField()
    recommendation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal_type} - {self.recommended_diet}"