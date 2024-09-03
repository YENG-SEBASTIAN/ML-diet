from django.contrib import admin
from account.models import UserProfile
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _('Diet Administration')
admin.site.index_title = _('Diet Recommendation Admin Dashboard')



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bmi', 'health_goal', 'weight', 'height')
