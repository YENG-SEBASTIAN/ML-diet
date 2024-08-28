from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
import plotly.graph_objs as go
import plotly.offline as pyo
from django.contrib.auth.decorators import login_required
from recommendations.models import Recommendation, UserRecommendationHistory, UserHealthHistroy
from account.models import UserProfile
import logging
from django.shortcuts import render
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

    # Query UserHealthHistroy for graph data
    health_history = UserHealthHistroy.objects.filter(user=request.user).order_by('id')

    # Initialize data for the graph
    dates = []
    heights = []
    weights = []
    bmis = []

    if health_history.exists():
        # Extract data for plotting if health history exists
        dates = [history.created_at for history in health_history]
        heights = [history.height for history in health_history]
        weights = [history.weight for history in health_history]
        bmis = [history.bmi for history in health_history]

    # Create Plotly graph
    fig = go.Figure()

    # Always add traces, even if they are empty
    fig.add_trace(go.Scatter(x=dates, y=heights, mode='lines+markers', name='Height (meters)'))
    fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', name='Weight (kg)'))
    fig.add_trace(go.Scatter(x=dates, y=bmis, mode='lines+markers', name='BMI'))

    fig.update_layout(
        title='User Health History',
        xaxis_title='Date',
        yaxis_title='Value',
        legend_title='Metrics'
    )

    # Convert Plotly figure to HTML
    graph_html = pyo.plot(fig, output_type='div')

    context = {
        'profile': profile,
        'graph_html': graph_html,
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
            user_profile.save()  # This will trigger the signal to create UserHealthHistory

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

@login_required
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



class RecommendationMetricsView(View):
    template_name = 'main/recommendation_metrics.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
