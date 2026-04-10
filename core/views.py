from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentCreateForm, ListingFilterForm, PostForm, ProfileForm, SignupForm
from .models import Comment, Like, Post, SavedListing, User


class RoomieLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


def app_home(request):
    return redirect("core:listing_list")


def signup(request):
    if request.user.is_authenticated:
        return redirect("core:listing_list")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:listing_list")
    else:
        form = SignupForm()
    return render(request, "core/app/signup.html", {"form": form})


def listing_list(request):
    queryset = Post.objects.select_related("author")
    form = ListingFilterForm(request.GET or None)

    if form.is_valid():
        data = form.cleaned_data
        q = data.get("q")
        listing_type = data.get("listing_type")
        location = data.get("location")
        min_price = data.get("min_price")
        max_price = data.get("max_price")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(location__icontains=q)
                | Q(lifestyle_notes__icontains=q)
            )
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

    return render(
        request,
        "core/app/listing_list.html",
        {
            "filter_form": form,
            "posts": queryset,
        },
    )


def listing_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    comments = post.comments.select_related("author").all()
    comment_form = CommentCreateForm()
    return render(
        request,
        "core/app/listing_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "is_liked": request.user.is_authenticated
            and Like.objects.filter(user=request.user, post=post).exists(),
            "is_saved": request.user.is_authenticated
            and SavedListing.objects.filter(user=request.user, post=post).exists(),
        },
    )


@login_required
def listing_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Listing created successfully.")
            return redirect("core:listing_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "core/app/listing_form.html", {"form": form, "page_title": "Create Listing"})


@login_required
def listing_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        return HttpResponseForbidden("You can only edit your own listings.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect("core:listing_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "core/app/listing_form.html", {"form": form, "page_title": "Edit Listing", "post": post})


@login_required
def listing_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        return HttpResponseForbidden("You can only delete your own listings.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect("core:listing_list")
    return render(request, "core/app/listing_confirm_delete.html", {"post": post})


def _safe_redirect_target(request, fallback):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect(_safe_redirect_target(request, reverse("core:listing_detail", kwargs={"pk": post.pk})))


@login_required
@require_POST
def toggle_save(request, pk):
    post = get_object_or_404(Post, pk=pk)
    saved, created = SavedListing.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved.delete()
    return redirect(_safe_redirect_target(request, reverse("core:listing_detail", kwargs={"pk": post.pk})))


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentCreateForm(request.POST)
    if form.is_valid():
        Comment.objects.create(
            post=post,
            author=request.user,
            content=form.cleaned_data["content"],
        )
    return redirect(_safe_redirect_target(request, reverse("core:listing_detail", kwargs={"pk": post.pk})))


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author_id != request.user.id:
        raise PermissionDenied("You can only delete your own comments.")
    post_id = comment.post_id
    comment.delete()
    return redirect(_safe_redirect_target(request, reverse("core:listing_detail", kwargs={"pk": post_id})))


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("core:profile_edit")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "core/app/profile_form.html", {"form": form})


@staff_member_required
def dashboard_home(request):
    context = {
        "stats": {
            "users_count": User.objects.count(),
            "posts_count": Post.objects.count(),
            "comments_count": Comment.objects.count(),
            "likes_count": Like.objects.count(),
            "saved_count": SavedListing.objects.count(),
        },
        "recent_posts": Post.objects.select_related("author")[:5],
        "recent_comments": Comment.objects.select_related("author", "post")[:5],
        "top_authors": User.objects.annotate(post_count=Count("posts")).order_by("-post_count", "username")[:5],
    }
    return render(request, "core/dashboard/home.html", context)
