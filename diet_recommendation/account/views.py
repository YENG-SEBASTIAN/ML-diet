from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re
from account.forms import UserProfileForm
from account.models import UserProfile
from django.contrib.auth.views import (PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, 
                                       PasswordResetDoneView, PasswordChangeView, PasswordChangeDoneView)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Validate that passwords match
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/signup.html')

        # Validate that password meets requirements
        password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$'
        if not re.match(password_pattern, password):
            messages.error(request, "Password does not meet requirements.")
            return render(request, 'auth/signup.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'auth/signup.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists.")
            return render(request, 'auth/signup.html')

        # Create user if everything is fine
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login')
    
    return render(request, 'auth/signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if next_url and next_url != request.path:
                return redirect(next_url)
            else:
                return redirect(reverse('dashboard'))
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')



@login_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        profile_image = request.FILES.get('profile_image')

        user = request.user

        # Basic validation
        if not username or not email:
            messages.error(request, "Username and Email are required.")
            return redirect('update_profile')

        try:
            user.username = username
            user.email = email

            if profile_image:
                user.profile_image = profile_image
            
            user.save()
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('update_profile')

    return render(request, 'main/settings.html')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Password reset link has been sent to your email.")
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been reset successfully. You can now log in.")
        return super().form_valid(form)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'main/settings.html'
    success_url = reverse_lazy('settings')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please correct the errors below.")
        return super().form_invalid(form)