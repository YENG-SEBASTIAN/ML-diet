from django.db import models
from django.contrib.auth.models import User

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_diet = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    bmi_at_time = models.FloatField()
    recommendation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recommendation for {self.user.username} on {self.recommendation_date}'


class DietPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return self.name


class UserRecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.SET_NULL, null=True)
    recommended_diet = models.CharField(max_length=255)
    recommendation_date = models.DateTimeField(auto_now_add=True)
    user_bmi = models.FloatField()
    user_health_goal = models.CharField(max_length=50)

    def __str__(self):
        return f'History for {self.user.username} on {self.recommendation_date}'




class DietRecommendationDataset(models.Model):
    recommended_diet = models.CharField(max_length=255)
    calories_kcal = models.IntegerField()
    protein_g = models.IntegerField()
    carbs_g = models.IntegerField()
    fat_g = models.IntegerField()
    health_benefits = models.TextField()
    suitable_age_group = models.CharField(max_length=255)
    meal_type = models.CharField(max_length=100)
    bmi = models.FloatField()
    bmi_category = models.CharField(max_length=100)

    def __str__(self):
        return self.recommended_diet