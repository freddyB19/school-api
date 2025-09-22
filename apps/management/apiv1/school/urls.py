from django.urls import path

from . import views

urlpatterns = [
	path(
		"<int:pk>/news/",
		views.NewsListCreateAPIView.as_view(),
		name = "news-list-create" 
	),
	path(
		"<int:pk>/officehour/",
		views.OfficeHourListCreateAPIView.as_view(),
		name = "officehour-list-create" 
	),
]