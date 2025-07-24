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
		exclude = ("school", )

class Settings(DjangoObjectType):
	colors = graphene.List(graphene.String())
	
	class Meta:
		model = models.SettingFormat
		exclude = ("colors", "school")

	def resolve_colors(obj, info):
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
	class Meta:
		model = models.Infraestructure
		exclude = ("school", ) 


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
		
		
		news = models.News.objects.filter(school_id = school_id)[:11]
		calendar = models.Calendar.objects.filter(school_id = school_id)[:11]
		socialMedia = models.SocialMedia.objects.filter(school_id = school_id)[:6]

		return SchoolHomePageType(
			school = school,
			news = news,
			calendar = calendar,
			settings = settings,
			networks = socialMedia
		)


	def resolve_schoolServiceOffline(root, info, schoolId):
		infraestructure = models.Infraestructure.objects.filter(school_id = schoolId)
		
		return ServiceOfflineType(
			infraestructure = infraestructure
		)


schema = graphene.Schema(query=Query)