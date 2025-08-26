from django.urls import path, include

from . import views
from .school.routers import router as school_router


app_name = "management"

urlpatterns = [
	path(
		"<int:pk>/", 
		views.AdministratorDetailAPIView.as_view(), 
		name = "administrator-detail"
	),
	path(
		"school/<int:school_id>/admin", 
		views.AdministratorAPIView.as_view(), 
		name = "administrator"
	),
	path(
		"user/<int:pk>/permission/", 
		views.UpdatePermissionsUser.as_view(), 
		name = "user-permission"
	),

	path('', include(school_router.urls)),
]
