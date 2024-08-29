from django.urls import path
from account import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-user-profile-info/', views.update_user_profile_info, name='update_user_profile_info'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

]
