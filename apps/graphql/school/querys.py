from django.utils import timezone

import graphene

from apps.school import models

from .types import (
	SchoolType,
	NewsType,
	CalendarType,
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


	def resolve_schoolBySubdomain(root, info, subdomain):
		try:
			school = models.School.objects.get(subdomain = subdomain)
		except models.School.DoesNotExist as e:
			return models.School.objects.none()

		school_id = school.id

		try:
			settings = models.SettingFormat.objects.get(school_id = school_id)
		except models.SettingFormat.DoesNotExist as e:
			settings = models.SettingFormat.objects.none()
		
		current_month = timezone.now().month
		
		news = models.News.objects.filter(school_id = school_id)[:10]
		calendar = models.Calendar.objects.filter(school_id = school_id, date__month = current_month)
		socialMedia = models.SocialMedia.objects.filter(school_id = school_id)
		coordinates = models.Coordinate.objects.filter(school_id = school_id)

		return SchoolHomePageType(
			school = school,
			news = news,
			calendar = calendar,
			settings = settings,
			networks = socialMedia,
			coordinates = coordinates
		)

	def resolve_schoolServiceOffline(root, info, schoolId):
		infraestructure = models.Infraestructure.objects.filter(
			school_id = schoolId
		)
		
		return ServiceOfflineType(
			infraestructure = infraestructure
		)

	def resolve_schoolServiceOnline(root, info, schoolId):
		downloads = models.Download.objects.filter(
			school_id = schoolId
		)[:11]

		repositories = models.Repository.objects.filter(
			school_id = schoolId
		)[:11]

		return ServiceOnlineType(
			downloads = downloads,
			repositories = repositories
		)
