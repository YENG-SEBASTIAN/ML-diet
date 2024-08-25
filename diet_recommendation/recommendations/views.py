from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
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


class DietRecommendationView(View):
    template_name = 'main/recommendation.html'

    def get(self, request, *args, **kwargs):
        # Query the last 10 recommendations for the user, ordered by recommendation_date
        recent_recommendations = Recommendation.objects.filter(
            user=request.user
        ).order_by('-recommendation_date')[:10]
        
        context = {
            'recommended_diets': recent_recommendations
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_bmi = request.POST.get('bmi')
        health_goal = request.POST.get('health_goal')

        if not user_bmi or not health_goal:
            messages.warning(request, "BMI and health goal are required.")
            return redirect('recommend_diet')

        try:
            user_bmi = float(user_bmi)
        except ValueError:
            messages.error(request, "Invalid BMI value.")
            return redirect('recommend_diet')

        try:
            # Get diet recommendations
            recommended_diets = recommend_diets(user_bmi, health_goal, n_recommendations=10)
            
            # Predict diet types
            predicted_diets = predict_diets(recommended_diets)
            
            if predicted_diets.empty:
                messages.info(request, "No diets found based on the provided criteria.")
                return redirect('recommend_diet')

            # Save the predicted diets to the Recommendation model
            for _, row in predicted_diets.iterrows():
                Recommendation.objects.create(
                    user=request.user,
                    recommended_diet=row['Predicted_Diet'],
                    calories=row['Calories_kcal'],
                    protein=row['Protein_g'],
                    carbs=row['Carbs_g'],
                    fat=row['Fat_g'],
                    bmi_at_time=row['BMI'],  # Use the input BMI value
                )
            
            # Query the last 10 recommendations for the user, ordered by recommendation_date
            recent_recommendations = Recommendation.objects.filter(
                user=request.user
            ).order_by('-recommendation_date')[:10]
            
            context = {
                'recommended_diets': recent_recommendations
            }

            return render(request, self.template_name, context)

        except Exception as e:
            logger.error(f"Error in diet recommendation view: {e}")
            messages.error(request, "An error occurred while processing your request.")
            return redirect('recommend_diet')



def settings(request):
    return render(request, 'main/settings.html')