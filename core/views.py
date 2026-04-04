from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


def app_home(request):
    return render(request, "core/app/home.html")


@staff_member_required
def dashboard_home(request):
    return render(request, "core/dashboard/home.html")
