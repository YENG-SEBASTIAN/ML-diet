from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from recommendations.models import (Recommendation, DietPlan, UserRecommendationHistory, 
                                    DietRecommendationDataset, UserHealthHistroy)
from recommendations.resources import (RecommendationResource, DietPlanResource, 
                                       UserRecommendationHistoryResource, DietRecommendationDatasetResource
)



@admin.register(Recommendation)
class RecommendationAdmin(ImportExportModelAdmin):
    resource_class = RecommendationResource
    list_display = ('user', 'recommended_diet', 'calories', 'protein', 'carbs', 'fat', 'bmi_at_time', 'recommendation_date')

@admin.register(DietPlan)
class DietPlanAdmin(ImportExportModelAdmin):
    resource_class = DietPlanResource
    list_display = ('name', 'description', 'calories', 'protein', 'carbs', 'fat')

@admin.register(UserRecommendationHistory)
class UserRecommendationHistoryAdmin(ImportExportModelAdmin):
    resource_class = UserRecommendationHistoryResource
    list_display = ('user', 'diet_plan', 'recommended_diet', 'recommendation_date', 'user_bmi', 'user_health_goal')




@admin.register(DietRecommendationDataset)
class DietRecommendationAdmin(ImportExportModelAdmin):
    resource_class = DietRecommendationDatasetResource
    list_display = ('recommended_diet', 'calories_kcal', 'protein_g', 'carbs_g', 'fat_g', 'bmi', 'bmi_category')
    search_fields = ('recommended_diet', 'meal_type', 'bmi_category')

admin.site.register(UserHealthHistroy)