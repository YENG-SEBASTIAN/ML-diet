from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import UserProfile
from recommendations.models import UserHealthHistroy

@receiver(post_save, sender=UserProfile)
def create_or_update_user_health_history(sender, instance, **kwargs):
    if instance.weight and instance.height:
        # Create a new UserHealthHistroy every time the UserProfile is saved
        UserHealthHistroy.objects.create(
            user=instance.user,
            weight=instance.weight,
            height=instance.height,
            bmi=instance.bmi,
            health_goal=instance.health_goal,
        )
