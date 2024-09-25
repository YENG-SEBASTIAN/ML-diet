from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import plotly.graph_objs as go
import plotly.offline as pyo
from django.contrib.auth.decorators import login_required
from recommendations.models import UserHealthHistory, DietRecommendation
from account.models import UserProfile
import logging
from django.shortcuts import render
from recommendations.ml_model import make_recommendation

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    user = request.user
    profile = None  # Initialize profile to None

    # Try to get the user's profile
    try:
        profile = UserProfile.objects.get(user=user)

        # Check if both weight and target_weight are non-zero and equal
        if profile.weight is not None and profile.target_weight is not None:
            if profile.weight != 0 and profile.target_weight != 0 and profile.weight == profile.target_weight:
                messages.success(request, "Congratulations! You have successfully achieved your target weight.")
            else:
                logger.error("User has not achieved target weight or profile values are not set correctly.")
        else:
            logger.debug("Profile values are None or zero, unable to determine target weight achievement.")

    except UserProfile.DoesNotExist:
        messages.error(request, "Your profile values are still zeros. Please complete your profile in the settings.")

    # Query UserHealthHistory for graph data
    health_history = UserHealthHistory.objects.filter(user=user).order_by('id')

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
        'profile': profile,  # This will be None if profile doesn't exist
        'graph_html': graph_html,
        'target_weight': profile.target_weight if profile else None,  # Only access target_weight if profile exists
    }

    return render(request, 'main/dashboard.html', context)


class DietRecommendationView(LoginRequiredMixin, View):
    template_name = 'main/recommendation.html'

    def get(self, request, *args, **kwargs):
        # Get or create the UserProfile for the user
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Retrieve the last 15 diet recommendations for the user, ordered by recommendation_date
        recent_recommendations = DietRecommendation.objects.filter(
            user=request.user
        ).order_by('-recommendation_date')[:15]

        # Check if the profile is complete
        profile_complete = all([
            profile.height is not None,
            profile.weight is not None,
            profile.health_goal
        ])

        # Prepare context for rendering the template
        context = {
            'recommended_diets': recent_recommendations,
            'profile_complete': profile_complete,
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
            messages.error(request, "Invalid height or weight value. Please enter valid numbers.")
            return redirect('recommend_diet')

        try:
            # Update or create the UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.weight = weight
            user_profile.height = height
            user_profile.health_goal = health_goal
            user_profile.save()  # This triggers the signal to create UserHealthHistory

            # Calculate BMI from UserProfile
            user_bmi = user_profile.bmi

            # Generate diet recommendations based on the user's BMI and health goal
            recommendations_df = make_recommendation(user_bmi, health_goal)

            # Save each recommendation to the database as a new object
            for _, row in recommendations_df.iterrows():
                DietRecommendation.objects.create(
                    user=request.user,
                    meal_type=row['Meal Type'],
                    recommended_diet=row['Recommended Diet'],
                    calories=row['Calories (kcal)'],
                    protein=row['Protein (g)'],
                    carbs=row['Carbs (g)'],
                    fat=row['Fat (g)'],
                    health_benefits=row['Health Benefits']
                )

            # Retrieve the last 15 diet recommendations for the user
            recent_recommendations = DietRecommendation.objects.filter(
                user=request.user
            ).order_by('-recommendation_date')[:15]

            # Check if the profile is complete
            profile_complete = all([
                user_profile.height is not None,
                user_profile.weight is not None,
                user_profile.health_goal
            ]) or not recent_recommendations.exists()

            # Add success message
            messages.success(request, "Your Diet recommendation was successful.")

            # Prepare context for rendering the template
            context = {
                'recommended_diets': recent_recommendations,
                'profile_complete': profile_complete,
            }

            return render(request, self.template_name, context)

        except Exception as e:
            logger.error(f"Error processing diet recommendation request: {e}")
            messages.error(request, "An error occurred while processing your request. Please try again.")
            return redirect('recommend_diet')



@login_required
def settings(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if created:
        messages.info(request, "Please update your profile.")

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
            start_index = 15
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
