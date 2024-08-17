from django.urls import path
from recommendations import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('recommend-diet/', views.diet_recommendation_view, name='recommend_diet'),

]
