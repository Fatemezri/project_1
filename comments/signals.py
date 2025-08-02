from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import Comment, Notification
from django.conf import settings
from django.db.utils import OperationalError

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=Comment)
def comment_post_save_handler(sender, instance, created, **kwargs):
    """
    This signal handler creates notifications for moderators and superusers
    when a comment is saved.
    """
    try:
        # Get the moderator group
        moderator_group = Group.objects.get(name='Moderators')

        # Get all users in the moderator group
        moderators = User.objects.filter(groups=moderator_group)

        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
    except (Group.DoesNotExist, OperationalError):
        # This can happen on the first migration before groups are created.
        # Log a warning or simply pass for now.
        print("Warning: Moderator group or users not found. Skipping signal.")
        return

    # A new comment has been created, notify the moderators.
    if created:
        for moderator in moderators:
            Notification.objects.create(
                recipient=moderator,
                sender=instance.user,
                notification_type='new_comment',
                message=f"New comment from {instance.user.username} is awaiting your approval.",
                related_comment=instance
            )

    # A comment has been approved, notify the superusers.
    if instance.status == 'approved' and 'status' in kwargs.get('update_fields', {}):
        for superuser in superusers:
            message = f"Comment by {instance.user.username} was approved by a moderator."
            if instance.moderator_report:
                message += f"\nModerator's Report: {instance.moderator_report}"

            Notification.objects.create(
                recipient=superuser,
                sender=instance.user,
                notification_type='comment_approved',
                message=message,
                related_comment=instance
            )
