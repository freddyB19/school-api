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
]