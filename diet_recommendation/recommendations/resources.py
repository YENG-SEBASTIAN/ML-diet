from import_export import resources
from .models import (DietRecommendation, DietPlan, UserHealthHistroy )

class DietRecommendationResource(resources.ModelResource):
    class Meta:
        model = DietRecommendation

class DietPlanResource(resources.ModelResource):
    class Meta:
        model = DietPlan


        
class UserHealthHistroyResource(resources.ModelResource):
    class Meta:
        model = UserHealthHistroy
