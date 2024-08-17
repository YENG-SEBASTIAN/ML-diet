from django.contrib import admin
from account.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bmi', 'health_goal', 'weight', 'height')
