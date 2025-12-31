from django.urls import path

from . import views

urlpatterns = [
	path(
		"<int:pk>/news/",
		views.NewsListCreateAPIView.as_view(),
		name = "news-list-create" 
	),
	path(
		"news/images/<int:pk>",
		views.NewsMediaDeleteAPIView.as_view(),
		name = "news-images-detail" 
	),
	path(
		"<int:pk>/officehour/",
		views.OfficeHourListCreateAPIView.as_view(),
		name = "officehour-list-create" 
	),
	path(
		"officehour/<int:pk>/",
		views.OfficeHourDetaiUpdateDeletelAPIView.as_view(),
		name = "officehour-detail" 
	),
	path(
		"<int:pk>/officehour/time",
		views.TimeGroupListAPIView.as_view(),
		name = "timegroup-list" 
	),
	path(
		"officehour/time/<int:pk>",
		views.TimeGroupDetailDeleteUpdateAPIView.as_view(),
		name = "timegroup-detail" 
	),
	path(
		"<int:pk>/calendar",
		views.CalendarListCreateAPIView.as_view(),
		name = "calendar-list-create" 
	),
	path(
		"calendar/<int:pk>",
		views.CalendarDetailDeleteUpdateAPIView.as_view(),
		name = "calendar-detail" 
	),
	path(
		"<int:pk>/socialmedia",
		views.SocialMediaListCreateAPIView.as_view(),
		name = "socialmedia-list-create" 
	),
	path(
		"socialmedia/<int:pk>",
		views.SocialMediaDetailDeleteUpdateAPIView.as_view(),
		name = "socialmedia-detail" 
	),
	path(
		"<int:pk>/coordinate",
		views.CoordinateListCreateAPIView.as_view(),
		name = "coordinate-list-create" 
	),
	path(
		"coordinate/<int:pk>",
		views.CoordinateDetailDeleteUpdateAPIView.as_view(),
		name = "coordinate-detail" 
	),
	path(
		"<int:pk>/staff",
		views.StaffListCreateAPIView.as_view(),
		name = "staff-list-create" 
	),
	path(
		"staff/<int:pk>",
		views.StaffDetailDeleteUpdateAPIView.as_view(),
		name = "staff-detail" 
	),
	path(
		"<int:pk>/grade",
		views.GradeListCreateAPIView.as_view(),
		name = "grade-list-create" 
	),
	path(
		"grade/<int:pk>",
		views.GradeDetailDeleteUpdateAPIView.as_view(),
		name = "grade-detail" 
	),
	path(
		"<int:pk>/repository",
		views.RepositoryListCreateAPIView.as_view(),
		name = "repository-list-create"
	),
]