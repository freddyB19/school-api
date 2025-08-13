from django.urls import path

from . import views
app_name = "management"

urlpatterns = [
	path(
		"<int:pk>/", 
		views.AdministratorDetailAPIView.as_view(), 
		name = "administrator-detail"
	),
	path(
		"school/<int:school_id>/", 
		views.AdministratorAPIView.as_view(), 
		name = "administrator"
	),
	path(
		"user/<int:pk>/permission/", 
		views.UpdatePermissionsUser.as_view(), 
		name = "user-permission"
	),

]
