from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)

from . import views

app_name = "user"

urlpatterns = [
    path(
        "<int:pk>/", 
        views.UserAPIView.as_view(), 
        name = "user"
    ),
    path(
        "<int:pk>/password/", 
        views.UserUpdatePasswordAPIView.as_view(), 
        name = "update-password"
    ),
    path(
        "<int:pk>/role/", 
        views.UserUpdateRoleAPIView.as_view(), 
        name = "update-role"
    ),
    path(
        "<int:pk>/reset/password/", 
        views.UserResetPasswordAPIView.as_view(), 
        name = "reset-password"
    ),

    path("login/", views.LoginAPIView.as_view(), name = "login"),
    path("register/", views.RegisterAPIView.as_view(), name = "register"),

     path("api/token/", TokenObtainPairView.as_view() ,name = "obtain_token_pair"),
     path("api/token/refresh/", TokenRefreshView.as_view(),name = "obtain_refresh"),
]
