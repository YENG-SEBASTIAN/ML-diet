from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import UserProfile
from recommendations.models import UserHealthHistroy

# Signal to create or update UserHealthHistroy after UserProfile is saved
@receiver(post_save, sender=UserProfile)
def create_or_update_user_health_history(sender, instance, created, **kwargs):
    if instance.weight and instance.height:
        UserHealthHistroy.objects.create(
            user=instance.user,
            weight=instance.weight,
            height=instance.height,
            bmi=instance.bmi,
            health_goal=instance.health_goal,
        )