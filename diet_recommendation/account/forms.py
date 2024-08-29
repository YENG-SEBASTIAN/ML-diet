# forms.py
from django import forms
from account.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['weight', 'height', 'health_goal', 'target_weight', 'health_condition', 'allergies']
