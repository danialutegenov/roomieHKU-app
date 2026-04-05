from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Post, Comment, Like, SavedListing

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'phone_number', 'profile_photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'phone_number', 'profile_photo')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(SavedListing)
