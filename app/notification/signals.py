from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a notification is created.
    """
    if created:
        # Add any logic you want to execute when a notification is created
        pass
