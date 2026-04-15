from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Post, Comment, Like, SavedListing

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("bio", "phone_number", "profile_photo", "is_suspended", "suspended_at")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("bio", "phone_number", "profile_photo")}),
    )
    list_display = ("username", "email", "is_staff", "is_active", "is_suspended")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "listing_type", "price", "is_hidden", "created_at")
    list_filter = ("listing_type", "is_hidden", "created_at")
    search_fields = ("title", "description", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "created_at")
    search_fields = ("author__username", "post__title", "content")


admin.site.register(Like)
admin.site.register(SavedListing)
