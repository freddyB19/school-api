from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType
from graphene_django import DjangoListField

from apps.school import models


class SchoolType(DjangoObjectType):
	class Meta:
		model = models.School
		fields = "__all__"


class NewsType(DjangoObjectType):
	photo = graphene.String()

	class Meta:
		model = models.News
		exclude = ("school", "media", "status", "description")

	def resolve_photo(obj, info):

		media = obj.media.first()
		return media.photo


class CalendarType(DjangoObjectType):
	class Meta:
		model = models.Calendar
		exclude = ("school", "description")


class Settings(DjangoObjectType):
	color = graphene.List(graphene.String)
	
	class Meta:
		model = models.SettingFormat
		exclude = ("colors", "school", "id")

	def resolve_color(obj, info):
		return [data.color for data in obj.colors.all()]


class SocialMediaType(DjangoObjectType):
	class Meta:
		model = models.SocialMedia
		fields = ("profile", )


class CoordinateType(DjangoObjectType):
	class Meta:
		model = models.Coordinate
		exclude = ("school", ) 


class InfraestructureType(DjangoObjectType):
	photo = graphene.String()
	
	class Meta:
		model = models.Infraestructure
		exclude = ("school", "description", "media") 

	def resolve_photo(obj, info):
		media = obj.media.first()
		return media.photo

class DownloadType(DjangoObjectType):
	class Meta:
		model = models.Download
		exclude = ("school", "description")


class RepositoryType(DjangoObjectType):
	project = graphene.String(required = True)

	class Meta:
		model = models.Repository
		exclude = ("school", "name_project", "media", "description")

	def resolve_project(obj, info):
		return obj.name_project


class SchoolHomePageType(graphene.ObjectType):
	school = graphene.Field(SchoolType)
	news = graphene.List(NewsType) # DjangoListField(NewsType)
	calendar = graphene.List(CalendarType) # DjangoListField(CalendarType)
	settings = graphene.Field(Settings)
	networks = graphene.List(SocialMediaType) # DjangoListField(SocialMediaType)
	coordinates = graphene.List(CoordinateType) # DjangoListField(CoordinateType)


class ServiceOnlineType(graphene.ObjectType):
	pass


class ServiceOfflineType(graphene.ObjectType):
	infraestructure = graphene.List(InfraestructureType) # DjangoListField(InfraestructureType)


class Query(graphene.ObjectType):
	schoolBySubdomain = graphene.Field(
		SchoolHomePageType, 
		subdomain = graphene.String(required = True)
	)

	schoolServiceOffline = graphene.Field(
		ServiceOfflineType,
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
		infraestructure = models.Infraestructure.objects.filter(school_id = schoolId)
		
		return ServiceOfflineType(
			infraestructure = infraestructure
		)


schema = graphene.Schema(query=Query)