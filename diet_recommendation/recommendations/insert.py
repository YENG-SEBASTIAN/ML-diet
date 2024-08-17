from recommendations.models import DietPlan, Recommendation, UserRecommendationHistory
# Sample diet plans
diet_plans = [
    {"name": "Low Carb Diet", "description": "A diet low in carbohydrates.", "calories": 1500, "protein": 120, "carbs": 50, "fat": 60},
    {"name": "High Protein Diet", "description": "A diet high in protein.", "calories": 1800, "protein": 200, "carbs": 100, "fat": 50},
    {"name": "Balanced Diet", "description": "A balanced diet with all nutrients.", "calories": 2000, "protein": 150, "carbs": 200, "fat": 70},
    {"name": "Vegan Diet", "description": "A diet excluding all animal products.", "calories": 1700, "protein": 100, "carbs": 220, "fat": 50},
    {"name": "Mediterranean Diet", "description": "A diet rich in fruits, vegetables, and healthy fats.", "calories": 2100, "protein": 130, "carbs": 230, "fat": 80},
]

# Create DietPlan instances
for plan in diet_plans:
    DietPlan.objects.create(**plan)



# Sample recommendations
recommendations = [
    {"user_id": 2, "recommended_diet": "High Protein Diet", "calories": 1800, "protein": 200, "carbs": 100, "fat": 50, "bmi_at_time": 22.3},
    {"user_id": 2, "recommended_diet": "Balanced Diet", "calories": 2000, "protein": 150, "carbs": 200, "fat": 70, "bmi_at_time": 25.1},
    {"user_id": 2, "recommended_diet": "Low Carb Diet", "calories": 1500, "protein": 120, "carbs": 50, "fat": 60, "bmi_at_time": 24.5},
    {"user_id": 2, "recommended_diet": "Vegan Diet", "calories": 1700, "protein": 100, "carbs": 220, "fat": 50, "bmi_at_time": 23.7},
    {"user_id": 2, "recommended_diet": "Mediterranean Diet", "calories": 2100, "protein": 130, "carbs": 230, "fat": 80, "bmi_at_time": 26.2},
]

# Create Recommendation instances
for recommendation in recommendations:
    Recommendation.objects.create(**recommendation)



# Sample user recommendation history
histories = [
    {"user_id": 2, "diet_plan_id": 1, "recommended_diet": "Low Carb Diet", "user_bmi": 24.5, "user_health_goal": "maintain weight"},
    {"user_id": 2, "diet_plan_id": 2, "recommended_diet": "High Protein Diet", "user_bmi": 22.3, "user_health_goal": "gain weight"},
    {"user_id": 2, "diet_plan_id": 3, "recommended_diet": "Balanced Diet", "user_bmi": 25.1, "user_health_goal": "maintain weight"},
    {"user_id": 2, "diet_plan_id": 4, "recommended_diet": "Vegan Diet", "user_bmi": 23.7, "user_health_goal": "lose weight"},
    {"user_id": 2, "diet_plan_id": 5, "recommended_diet": "Mediterranean Diet", "user_bmi": 26.2, "user_health_goal": "maintain weight"},
]

# Create UserRecommendationHistory instances
for history in histories:
    UserRecommendationHistory.objects.create(**history)
