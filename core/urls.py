from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.app_home, name="home"),
    path("app/", views.app_home, name="app_home"),
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
]
