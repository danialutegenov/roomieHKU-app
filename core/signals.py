from django.db.models import Case, F, IntegerField, Value, When
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Like, Post


@receiver(post_save, sender=Like)
def increment_post_likes_count(sender, instance, created, **kwargs):
    if not created:
        return
    Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") + 1)


@receiver(post_delete, sender=Like)
def decrement_post_likes_count(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(
        likes_count=Case(
            When(likes_count__gt=0, then=F("likes_count") - 1),
            default=Value(0),
            output_field=IntegerField(),
        )
    )
