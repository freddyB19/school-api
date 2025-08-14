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


SchoolDoesNotExist = None

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
			school = models.School.objects..get(subdomain = subdomain)
		except models.School.DoesNotExist as e:
			return SchoolDoesNotExist

		current_month = timezone.now().month

		settings = school.setting
		calendar = school.calendarsList.filter(date__month = current_month)
		news = school.newsList.filter(status = "publicado")[:10]		
		socialMedia = school.socialMediasList.all()[:6]
		coordinates = school.coordinatesList.all()

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
