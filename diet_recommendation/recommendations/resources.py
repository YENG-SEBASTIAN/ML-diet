from import_export import resources
from .models import (DietRecommendation, DietPlan, UserHealthHistory )

class DietRecommendationResource(resources.ModelResource):
    class Meta:
        model = DietRecommendation

class DietPlanResource(resources.ModelResource):
    class Meta:
        model = DietPlan


        
class UserHealthHistoryResource(resources.ModelResource):
    class Meta:
        model = UserHealthHistory
