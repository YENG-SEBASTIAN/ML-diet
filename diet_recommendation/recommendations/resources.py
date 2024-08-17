from import_export import resources
from .models import (Recommendation, DietPlan, UserRecommendationHistory,
                     DietRecommendationDataset )

class RecommendationResource(resources.ModelResource):
    class Meta:
        model = Recommendation

class DietPlanResource(resources.ModelResource):
    class Meta:
        model = DietPlan

class UserRecommendationHistoryResource(resources.ModelResource):
    class Meta:
        model = UserRecommendationHistory
        
class DietRecommendationDatasetResource(resources.ModelResource):
    class Meta:
        model = DietRecommendationDataset
