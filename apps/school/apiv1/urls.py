from django.urls import path

from . import views
app_name = "school"


urlpatterns = [
	path(
		"", 
		views.SchoolAPIView.as_view(), 
		name='school'
	),
	path(
		"<int:pk>/", 
		views.SchoolDetailAPIView.as_view(), 
		name='detail'
	),
	path(
		"settings/<int:pk>/", 
		views.SettingsFormatAPIView.as_view(), 
		name='settings'
	),
	path(
		"<int:pk>/office/", 
		views.OfficeHourList.as_view(), 
		name='office-hour'
	),
	path(
		"office/<int:pk>/", 
		views.OfficeHourDetailAPIView.as_view(), 
		name='office-hour-detail'
	),
	path(
		"<int:pk>/calendar", 
		views.CalendarListAPIView.as_view(), 
		name='calendar'
	),
	path(
		"calendar/<int:pk>/", 
		views.CalendarDetailAPIView.as_view(), 
		name='calendar-detail'
	),
	path(
		"<int:pk>/social/media/", 
		views.SocialMediaListAPIView.as_view(), 
		name='social-media'
	),
	path(
		"<int:pk>/coordinate/", 
		views.CoordinateListAPIView.as_view(), 
		name='coordinate'
	),
	path(
		"<int:pk>/grade", 
		views.GradesListAPiView.as_view(), 
		name='grade'
	),
	path(
		"grade/<int:pk>/", 
		views.GradeDetailAPIView.as_view(), 
		name='grade-detail'
	),
	path(
		"<int:pk>/repository/", 
		views.RepositoryListAPIView.as_view(), 
		name='repository'
	),
	path(
		"repository/<int:pk>/", 
		views.RepositoryDetailAPIView.as_view(), 
		name='repository-detail'
	),
	# path(
	# 	"<int:pk>/service/", 
	# 	views.SchoolServiceAPIView.as_view(), 
	# 	name='school-services'
	# ),
	path(
		"<int:pk>/infraestructure/", 
		views.InfraestructureListAPIView.as_view(), 
		name='infraestructure'
	),
	path(
		"infraestructure/<int:pk>/", 
		views.InfraestructureDetailAPIView.as_view(), 
		name='infraestructure-detail'
	),
	path(
		"<int:pk>/download/", 
		views.DownloadsListAPIView.as_view(), 
		name='downloads'
	),
	path(
		"download/<int:pk>/", 
		views.DownloadsDetailAPIView.as_view(), 
		name='downloads-detail'
	),
	path(
		"<int:pk>/news/", 
		views.NewsListAPIView.as_view(), 
		name='news'
	),
	path(
		"news/<int:pk>/", 
		views.NewsDetailAPIView.as_view(), 
		name='news-detail'
	),
	path(
		"<int:pk>/cultural/event/", 
		views.CulturalEventsListAPIView.as_view(), 
		name='cultural-events'
	),
	path(
		"cultural/event/<int:pk>/", 
		views.CulturalEventsDetailAPIView.as_view(), 
		name='cultural-events-detail'
	),
	path(
		"<int:pk>/payment/info/", 
		views.PaymentInfoAPIView.as_view(), 
		name='payment-info'
	),
	path(
		"<int:pk>/contact/", 
		views.ContactInfoAPIView.as_view(), 
		name='contact-info'
	),
	path(
		"<int:pk>/extra/activity/", 
		views.ExtraActivitiesListAPIView.as_view(), 
		name='extra-activitie'
	),
	path(
		"extra/activity/<int:pk>/", 
		views.ExtraActivitiesDetailAPIView.as_view(), 
		name='extra-activitie-detail'
	),
]

