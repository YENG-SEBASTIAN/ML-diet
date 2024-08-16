from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re

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
            messages.error(request, "Email already exists.")
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
            # Redirect to 'next' if valid, otherwise to 'dashboard_view'
            if next_url and next_url != request.path:
                return redirect(next_url)
            else:
                return redirect(reverse('dashboard_view'))
        else:
            messages.error(request, "Invalid username or password.")
            # Re-render login page with error messages
            return render(request, 'auth/login.html')

    # Handle GET requests or other request methods
    return render(request, 'auth/login.html')

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')
