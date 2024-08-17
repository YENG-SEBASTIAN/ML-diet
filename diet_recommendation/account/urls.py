from django.urls import path
from account import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),

]
