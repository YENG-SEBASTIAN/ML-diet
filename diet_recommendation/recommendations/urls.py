from django.urls import path
from recommendations import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('recommend-diet/', views.DietRecommendationView.as_view(), name='recommend_diet'),
    path('diet-plan/', views.DietPlainView.as_view(), name='diet_plan'),
    path('metrics/', views.RecommendationMetricsView.as_view(), name='recommendation_metrics'),

]
