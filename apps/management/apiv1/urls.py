from django.urls import path, include

from . import views
from .school.routers import router as school_router
from .school.urls import urlpatterns as school_urls



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
		views.UpdateUserPermissions.as_view(), 
		name = "user-permission"
	),

	path('school/', include(school_urls)),
	path('', include(school_router.urls)),

]