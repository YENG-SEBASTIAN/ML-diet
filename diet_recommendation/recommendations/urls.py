
from django.urls import path
from recommendations.views import RecommendDiet

urlpatterns = [
    path('recommend/', RecommendDiet.as_view(), name='recommend_diet'),
]