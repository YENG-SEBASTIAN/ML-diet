from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import plotly.graph_objs as go
import plotly.offline as pyo
from django.contrib.auth.decorators import login_required
from recommendations.models import UserHealthHistroy, DietRecommendation
from account.models import UserProfile
import logging
from django.shortcuts import render
from recommendations.ml_model import make_recommendation

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    user = request.user
    # Try to get the user's profile
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Your profile values are still zeros. Please complete your profile at the settings.")
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

    # Add traces for graph
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
        'target_weight': profile.target_weight,
    }

    return render(request, 'main/dashboard.html', context)

class DietRecommendationView(LoginRequiredMixin, View):
    template_name = 'main/recommendation.html'

    def get(self, request, *args, **kwargs):
        # Query the last 10 recommendations for the user, ordered by recommendation_date
        recent_recommendations = DietRecommendation.objects.filter(
            user=request.user
        ).order_by('-recommendation_date')[:15]

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

            recommendations_df = make_recommendation(user_bmi, health_goal)

            for _, row in recommendations_df.iterrows():
                recommendation = DietRecommendation(
                    user=request.user,  # Associate the recommendation with the current user
                    meal_type=row['Meal Type'],
                    recommended_diet=row['Recommended Diet'],
                    calories=row['Calories (kcal)'],
                    protein=row['Protein (g)'],
                    carbs=row['Carbs (g)'],
                    fat=row['Fat (g)'],
                    vitamins=row['Vitamins'],
                    minerals=row['Minerals'],
                    health_benefits=row['Health Benefits']
                )
                recommendation.save()

            # Query the last 10 recommendations for the user, ordered by recommendation_date
            recent_recommendations = DietRecommendation.objects.filter(
                user=request.user
            ).order_by('-recommendation_date')[:15]

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
    user_profile = UserProfile.objects.get(user=request.user)
    print("user_profile", user_profile)
    context = {
        'userprofile': user_profile,
    }
    return render(request, 'main/settings.html', context)

class DietPlainView(LoginRequiredMixin, View):
    template_name = 'main/diet_plain.html'

    def get(self, request, *args, **kwargs):
        # Filter recommendations for the logged-in user
        user_recommendations = DietRecommendation.objects.filter(user=request.user).order_by('-recommendation_date')
        
        # Get the total count of the user's recommendations
        total_count = user_recommendations.count()
        
        # Calculate the start index for the slice of recommendations
        if total_count >= 30:
            start_index = total_count -15
        else:
            start_index = 0
        # Fetch 15 objects before the last 15 objects
        recommendations_before_last_15 = user_recommendations[start_index:]
        
        context = {
            'recommended_diets': recommendations_before_last_15
        }
        
        return render(request, self.template_name, context)



class RecommendationMetricsView(LoginRequiredMixin, View):
    template_name = 'main/recommendation_metrics.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
