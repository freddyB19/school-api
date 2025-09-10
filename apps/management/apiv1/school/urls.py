from django.urls import path

from . import views

urlpatterns = [
	path(
		"<int:school_id>/news/",
		views.NewsListCreateAPIView.as_view(),
		name = "news-list-create" 
	)
]