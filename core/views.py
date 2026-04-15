from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Comment, Post, SavedListing

User = get_user_model()


def app_home(request):
    return render(request, "core/app/home.html")


@staff_member_required
def dashboard_home(request):
    total_users = User.objects.count()
    total_listings = Post.objects.count()
    total_comments = Comment.objects.count()

    users = User.objects.all().order_by("-date_joined")
    listings = Post.objects.select_related("author").all().order_by("-created_at")
    comments = Comment.objects.select_related("author", "post").all().order_by("-created_at")

    most_saved_listings = (
        Post.objects.annotate(saved_count=Count("saved_by"))
        .select_related("author")
        .order_by("-saved_count", "-created_at")[:10]
    )

    most_active_users = (
        User.objects.annotate(
            post_count=Count("posts", distinct=True),
            comment_count=Count("comment", distinct=True),
        )
        .annotate(total_activity=F("post_count") + F("comment_count"))
        .order_by("-total_activity", "-date_joined")[:10]
    )

    context = {
        "total_users": total_users,
        "total_listings": total_listings,
        "total_comments": total_comments,
        "users": users,
        "listings": listings,
        "comments": comments,
        "most_saved_listings": most_saved_listings,
        "most_active_users": most_active_users,
    }
    return render(request, "core/dashboard/home.html", context)


@staff_member_required
def hide_listing(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        post.is_hidden = True
        post.hidden_at = timezone.now()
        post.save(update_fields=["is_hidden", "hidden_at"])
        messages.success(request, "Listing hidden successfully.")
    return redirect("core:dashboard_home")


@staff_member_required
def reactivate_listing(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        post.is_hidden = False
        post.hidden_at = None
        post.save(update_fields=["is_hidden", "hidden_at"])
        messages.success(request, "Listing reactivated successfully.")
    return redirect("core:dashboard_home")


@staff_member_required
def delete_listing(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        messages.success(request, "Listing deleted successfully.")
    return redirect("core:dashboard_home")


@staff_member_required
def suspend_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)
        user.is_suspended = True
        user.suspended_at = timezone.now()
        user.save(update_fields=["is_suspended", "suspended_at"])
        messages.success(request, "User suspended successfully.")
    return redirect("core:dashboard_home")


@staff_member_required
def reactivate_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)
        user.is_suspended = False
        user.suspended_at = None
        user.save(update_fields=["is_suspended", "suspended_at"])
        messages.success(request, "User reactivated successfully.")
    return redirect("core:dashboard_home")


@staff_member_required
def delete_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    return redirect("core:dashboard_home")
