from django.urls import path

from . import views

urlpatterns = [
	path("", views.test_view_email, name = "email-reset-password")
]