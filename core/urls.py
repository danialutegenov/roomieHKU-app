from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.app_home, name="home"),
    path("app/", views.app_home, name="app_home"),
    path("auth/login/", views.RoomieLoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(next_page="core:listing_list"), name="logout"),
    path("auth/signup/", views.signup, name="signup"),
    path("app/listings/", views.listing_list, name="listing_list"),
    path("app/listings/new/", views.listing_create, name="listing_create"),
    path("app/listings/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("app/listings/<int:pk>/edit/", views.listing_update, name="listing_update"),
    path("app/listings/<int:pk>/delete/", views.listing_delete, name="listing_delete"),
    path("app/listings/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path("app/listings/<int:pk>/save/", views.toggle_save, name="toggle_save"),
    path("app/listings/<int:pk>/comments/add/", views.add_comment, name="add_comment"),
    path("app/comments/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("app/profile/edit/", views.profile_edit, name="profile_edit"),
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
]
