from django.urls import path
from recommendations import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('recommend-diet/', views.get_diet_recommendations, name='recommend_diet'),

]
