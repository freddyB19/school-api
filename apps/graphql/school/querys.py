import datetime
from django.utils import timezone

import graphene
from graphene import relay

from apps.school import models

from .types import (
	Months,
	SchoolType,
	NewsType,
	CalendarConnection,
	SettingsType,
	SocialMediaType,
	CoordinateType,
	InfraestructureType,
	DownloadType,
	RepositoryType,
	SchoolHomePageType,
	ServiceOnlineType,
	ServiceOfflineType

)


class SchoolQuery(graphene.ObjectType):
	schoolBySubdomain = graphene.Field(
		SchoolHomePageType, 
		subdomain = graphene.String(required = True)
	)

	schoolServiceOffline = graphene.Field(
		ServiceOfflineType,
		schoolId = graphene.Int(required = True)
	)

	schoolServiceOnline = graphene.Field(
		ServiceOnlineType,
		schoolId = graphene.Int(required = True)
	)

	schoolCalendar = relay.ConnectionField(
		CalendarConnection,
		subdomain = graphene.String(required = True),
		month = graphene.Argument(Months)
	)


	def resolve_schoolBySubdomain(root, info, subdomain):
		school = models.School.objects.filter(subdomain = subdomain).first()
		if not school:
			return models.School.objects.none()

		settings = models.SettingFormat.objects.get(school_id = school.id)
		news = models.News.objects.filter(school_id = school.id)[:10]		
		socialMedia = models.SocialMedia.objects.filter(school_id = school.id)
		coordinates = models.Coordinate.objects.filter(school_id = school.id)

		return SchoolHomePageType(
			school = school,
			news = news,
			settings = settings,
			networks = socialMedia,
			coordinates = coordinates
		)


	def resolve_schoolCalendar(root, info, subdomain, month = None, **kwargs):
		school = models.School.objects.filter(subdomain = subdomain).first()
		if not school:
			return models.School.objects.none()

		current_time = timezone.localtime()

		search_month = current_time.month if not month else Months.get(month).value
		search_year = current_time.year

		list_calendar = models.Calendar.objects.filter(
			school_id = school.id,
			date__month = search_month,
			date__year = search_year
		).order_by("date")

		return list_calendar
	

	def resolve_schoolServiceOffline(root, info, schoolId):
		MAX_LEN_SERVICE_OFFLINE = 11

		infraestructures = models.Infraestructure.objects.filter(
			school_id = schoolId
		)[:MAX_LEN_SERVICE_OFFLINE]
		
		return ServiceOfflineType(
			infraestructures = infraestructures
		)


	def resolve_schoolServiceOnline(root, info, schoolId):
		MAX_LEN_SERVICE_ONLINE = 11

		downloads = models.Download.objects.filter(
			school_id = schoolId
		)[:MAX_LEN_SERVICE_ONLINE]

		repositories = models.Repository.objects.filter(
			school_id = schoolId
		)[:MAX_LEN_SERVICE_ONLINE]

		return ServiceOnlineType(
			downloads = downloads,
			repositories = repositories
		)
