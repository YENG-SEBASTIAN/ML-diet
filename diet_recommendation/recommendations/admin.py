from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from recommendations.models import (DietPlan, UserHealthHistory, DietRecommendation)
from recommendations.resources import (DietPlanResource, DietRecommendationResource,
                                       UserHealthHistoryResource)

@admin.register(DietPlan)
class DietPlanAdmin(ImportExportModelAdmin):
    resource_class = DietPlanResource
    list_display = ('name', 'description', 'calories', 'protein', 'carbs', 'fat')
    
class UserHealthHistoryAdmin(ImportExportModelAdmin):
    resource_class = UserHealthHistoryResource
    list_display = ('user', 'weight', 'height', 'bmi', 'health_goal', 'created_at')
    search_fields = ('user__username', 'health_goal')
    list_filter = ('health_goal', 'created_at')

class DietRecommendationAdmin(ImportExportModelAdmin):
    resource_class = DietRecommendationResource
    list_display = ('user', 'meal_type', 'recommended_diet', 'calories', 'protein', 'carbs', 'fat', 'recommendation_date')
    search_fields = ('user__username', 'meal_type', 'recommended_diet')
    list_filter = ('meal_type', 'recommendation_date')
    readonly_fields = ('recommendation_date',)

admin.site.register(UserHealthHistory, UserHealthHistoryAdmin)
admin.site.register(DietRecommendation, DietRecommendationAdmin)