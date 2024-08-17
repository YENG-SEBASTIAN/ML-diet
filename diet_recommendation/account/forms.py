from django import forms
from account.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bmi', 'health_goal', 'weight', 'height']
        widgets = {
            'health_goal': forms.Select(choices=UserProfile.HEALTH_GOAL_CHOICES),
        }
