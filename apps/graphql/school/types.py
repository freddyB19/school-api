import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django import DjangoListField

from apps.school import models


class Months(graphene.Enum):
	ENE = 1
	FEB = 2
	MAR = 3
	ABR = 4
	MAY = 5
	JUN = 6
	JUL = 7
	AGO = 8
	SEP = 9
	OCT = 10
	NOV = 11
	DIC = 12


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
	calendarId = graphene.Int()

	class Meta:
		model = models.Calendar
		exclude = ("school", "description")
		interfaces = (relay.Node, )

	def resolve_calendarId(obj, info):
		return obj.id


class CalendarConnection(relay.Connection):

	class Meta:
		node = CalendarType


class SettingsType(DjangoObjectType):
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
	settings = graphene.Field(SettingsType)
	networks = graphene.List(SocialMediaType) # DjangoListField(SocialMediaType)
	coordinates = graphene.List(CoordinateType) # DjangoListField(CoordinateType)


class ServiceOnlineType(graphene.ObjectType):
	downloads = graphene.List(DownloadType) # DjangoListField(DownloadType)
	repositories = graphene.List(RepositoryType) # DjangoListField(RepositoryType)


class ServiceOfflineType(graphene.ObjectType):
	infraestructure = graphene.List(InfraestructureType) # DjangoListField(InfraestructureType)
