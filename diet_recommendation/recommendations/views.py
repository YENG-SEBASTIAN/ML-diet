from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'main/dashboard.html')

def settings(request):
    return render(request, 'main/settings.html')