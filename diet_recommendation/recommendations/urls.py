from django.urls import path
from recommendations import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
]
