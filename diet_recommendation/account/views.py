from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re
from account.forms import UserProfileForm
from account.models import UserProfile

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
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('main/profile_update_success')  # Redirect to a success page or profile view
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'main/update_profile.html', {'form': form})


@login_required
def profile_update_success(request):
    return render(request, 'main/profile_update_success.html')