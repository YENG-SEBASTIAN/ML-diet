from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.db.models import Count, Avg, Sum
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
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        health_goal = request.POST.get('health_goal')

        if not height or not weight or not health_goal:
            messages.warning(request, "Height, weight, and health goal are required.")
            return redirect('recommend_diet')

        try:
            height = float(height)
            weight = float(weight)
        except ValueError:
            messages.error(request, "Invalid height or weight value.")
            return redirect('recommend_diet')

        try:
            # Update or create the UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.weight = weight
            user_profile.height = height
            user_profile.health_goal = health_goal
            user_profile.save()

            # Calculate BMI from UserProfile
            user_bmi = user_profile.bmi

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
                    bmi_at_time=row['BMI'],
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

class DietPlainView(View):
    template_name = 'main/diet_plain.html'

    def get(self, request, *args, **kwargs):
        # Query the last 10 recommendations for the user, ordered by recommendation_date
        recent_recommendations = Recommendation.objects.filter(
            user=request.user
        ).order_by('-recommendation_date')[:10]
        
        context = {
            'recommended_diets': recent_recommendations
        }
        return render(request, self.template_name, context)


def metrics(request):
    return render(request, 'main/settings.html')

class RecommendationMetricsView(View):
    template_name = 'main/recommendation_metrics.html'

    def get(self, request, *args, **kwargs):
        # Calculate metrics
        total_recommendations = Recommendation.objects.count()
        avg_calories = Recommendation.objects.aggregate(Avg('calories'))['calories__avg']
        avg_protein = Recommendation.objects.aggregate(Avg('protein'))['protein__avg']
        avg_carbs = Recommendation.objects.aggregate(Avg('carbs'))['carbs__avg']
        avg_fat = Recommendation.objects.aggregate(Avg('fat'))['fat__avg']

        context = {
            'total_recommendations': total_recommendations,
            'avg_calories': avg_calories,
            'avg_protein': avg_protein,
            'avg_carbs': avg_carbs,
            'avg_fat': avg_fat,
        }
        return render(request, self.template_name, context)