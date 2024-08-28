from django.urls import path
from account import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

]
