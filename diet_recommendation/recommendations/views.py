from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from recommendations.models import Recommendation, UserRecommendationHistory
from account.models import UserProfile
import json
from recommendations.ml_model import recommend_diets

@login_required
def dashboard_view(request):
    user = request.user
    
    # Try to get the user's profile
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile does not exist. Please complete your profile.")
        return redirect('update_profile')  # Redirect to a profile update page if the profile does not exist
    
    # Try to get the latest recommendation
    latest_recommendation = Recommendation.objects.filter(user=user).order_by('-recommendation_date').first()
    if not latest_recommendation:
        messages.warning(request, "No recommendation found. Please check back later or request one.")
    
    # Get user recommendation history (last 7 entries)
    history = UserRecommendationHistory.objects.filter(user=user).order_by('-recommendation_date')[:7]
    if not history:
        messages.info(request, "No recommendation history available.")
    
    # Fetch recommendations for chart
    recommendations = Recommendation.objects.filter(user=user).order_by('-recommendation_date')
    recommendation_data = {
        "dates": [],
        "calories": [],
        "protein": [],
        "carbs": [],
        "fat": []
    }
    for rec in recommendations:
        recommendation_data["dates"].append(rec.recommendation_date.strftime('%Y-%m-%d'))
        recommendation_data["calories"].append(rec.calories)
        recommendation_data["protein"].append(rec.protein)
        recommendation_data["carbs"].append(rec.carbs)
        recommendation_data["fat"].append(rec.fat)
    
    context = {
        'profile': profile,
        'latest_recommendation': latest_recommendation,
        'history': history,
        'recommendation_data': json.dumps(recommendation_data)
    }
    
    return render(request, 'main/dashboard.html', context)



def diet_recommendation_view(request):
    if request.method == 'POST':
        # Retrieve user input from the form
        user_bmi = float(request.POST.get('bmi'))
        health_goal = request.POST.get('health_goal')

        # Get diet recommendations
        recommended_diets = recommend_diets(user_bmi, health_goal, n_recommendations=10)

        # Render the results in the template
        return render(request, 'main/recommendation.html', {
            'recommended_diets': recommended_diets
        })

    # Render the form if not a POST request
    return render(request, 'main/recommendation.html')


def settings(request):
    return render(request, 'main/settings.html')