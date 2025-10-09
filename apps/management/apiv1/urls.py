from django.urls import path, include

from . import views
from .school.routers import router as school_router
from .school.urls import urlpatterns as school_urls
from .user.urls import urlpatterns as user_urls


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
	path('school/', include(school_urls)),
	path('', include(school_router.urls)),

	path('user/', include(user_urls)),
]