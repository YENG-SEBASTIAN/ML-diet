from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from recommendations.models import Recommendation, UserRecommendationHistory
from account.models import UserProfile
import json
import logging

from recommendations.ml_model import recommend_diets, predict_diets

logger = logging.getLogger(__name__)



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


def get_diet_recommendations(request):
    if request.method == 'POST':
        user_bmi = request.POST.get('bmi')
        health_goal = request.POST.get('health_goal')

        if not user_bmi or not health_goal:
            messages.warning(request, "BMI and health goal are required.")
            return render(request, 'main/recommendation.html')

        try:
            user_bmi = float(user_bmi)
        except ValueError:
            messages.error(request, "Invalid BMI value.")
            return render(request, 'main/recommendation.html')

        try:
            # Get diet recommendations
            recommended_diets = recommend_diets(user_bmi, health_goal, n_recommendations=10)
            
            # Predict diet types
            predicted_diets = predict_diets(recommended_diets)
            if recommended_diets.empty:
                messages.info(request, "No diets found based on the provided criteria.")
            else:
                # Convert DataFrame to a list of dictionaries for rendering
                context = {
                    'recommended_diets': predicted_diets.to_dict(orient='records')
                }


            return render(request, 'main/recommendation.html', context)

        except Exception as e:
            logger.error(f"Error in diet recommendation view: {e}")
            return render(request, 'main/recommendation.html', {
                'error_message': "An error occurred while processing your request."
            })

    return render(request, 'main/recommendation.html')



def settings(request):
    return render(request, 'main/settings.html')