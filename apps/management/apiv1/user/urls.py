from django.urls import path

from . import views

urlpatterns = [
    path(
        "", 
        views.CreateUserAPIView.as_view(), 
        name = "user-create"
    ),
    path(
        "login", 
        views.LoginUserAPIView.as_view(), 
        name = "login"
    ),
	path(
		"<int:pk>/permission", 
		views.UpdateUserPermissions.as_view(), 
		name = "user-permission"
	),
	path(
        "<int:pk>/role", 
        views.UpdateUserRoleAPIView.as_view(), 
        name = "user-role-update"
    ),
]