
from enum import IntEnum

import strawberry, strawberry_django

from strawberry import auto, relay

from apps.school import models


@strawberry.enum
class MonthsEnum(IntEnum):
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

@strawberry_django.filter_type(models.School)
class SchoolFilter:
	id: auto
	subdomain: auto

@strawberry_django.type(models.School, filters=SchoolFilter)
class School:
	id: auto
	name: auto
	subdomain: auto
	logo: auto
	address: auto
	mission: auto
	vision: auto
	history: auto
	private: auto


@strawberry_django.filter_type(models.News)
class NewsFilter:
	school: SchoolFilter | None

@strawberry_django.order_type(models.News)
class NewsOrder:
	created: auto
	updated: auto

@strawberry_django.type(models.NewsMedia)
class NewsMedia:
	photo: auto


@strawberry_django.type(models.News, filters = NewsFilter, ordering = NewsOrder)
class News(relay.Node):
	id: auto
	title: auto
	created: auto
	updated: auto
	media: list[NewsMedia] = strawberry_django.field(
		prefetch_related = "media"
	) 



@strawberry_django.order_type(models.Calendar)
class CalendarOrder:
	date: auto

@strawberry_django.filter_type(models.Calendar)
class CalendarFilter:
	school: SchoolFilter | None

@strawberry_django.type(models.Calendar)
class Calendar:
	id: auto
	title: auto
	date: auto


@strawberry_django.type(models.ColorHexFormat)
class ColorHexFormat:
	color: auto

@strawberry_django.filter_type(models.SettingFormat)
class SettingFormatFilter:
	school: SchoolFilter | None


@strawberry_django.type(models.SettingFormat, filters = SettingFormatFilter)
class SettingFormat:
	colors: list[ColorHexFormat]



@strawberry_django.filter_type(models.SocialMedia)
class SocialMediaFilter:
	school: SchoolFilter | None


@strawberry_django.type(models.SocialMedia, filters = SocialMediaFilter)
class SocialMedia:
	profile: auto


@strawberry_django.order_type(models.Coordinate)
class CoordinateOrder:
	title: auto

@strawberry_django.filter_type(models.Coordinate)
class CoordinateFilter:
	school: SchoolFilter | None


@strawberry_django.type(models.Coordinate, filters = CoordinateFilter, ordering = CoordinateOrder)
class Coordinate(relay.Node):
	id: auto
	title: auto
	latitude: auto
	longitude: auto


@strawberry_django.order_type(models.Infraestructure)
class InfraestructureOrder:
	name: auto


@strawberry_django.filter_type(models.Infraestructure)
class InfraestructureFilter:
	school: SchoolFilter | None


@strawberry_django.type(models.InfraestructureMedia)
class InfraestructureMedia:
	photo: auto


@strawberry_django.type(models.Infraestructure, filters = InfraestructureFilter, ordering = InfraestructureOrder)
class Infraestructure(relay.Node):
	id: strawberry.relay.GlobalID
	name: auto
	media: list[InfraestructureMedia] = strawberry_django.field(
		prefetch_related = ["media"]
	)


@strawberry_django.order_type(models.Download)
class DownloadOrder:
	title: auto

@strawberry_django.filter_type(models.Download)
class DownloadFilter:
	school: SchoolFilter | None

@strawberry_django.type(models.Download, filters = DownloadFilter, ordering = DownloadOrder)
class Download(relay.Node):
	id: auto
	title: auto
	file: auto


@strawberry_django.order_type(models.Repository)
class RepositoryOrder:
	created:auto
	updated: auto


@strawberry_django.filter_type(models.Repository)
class RepositoryFilter:
	school: SchoolFilter | None


@strawberry_django.type(models.RepositoryMediaFile)
class RepositoryMediaFile:
	title: auto
	file: auto


@strawberry_django.type(models.Repository, filters = RepositoryFilter, ordering = RepositoryOrder)
class Repository(relay.Node):
	id: auto
	name_project: auto
	created: auto
	updated: auto
	media: list[RepositoryMediaFile] = strawberry_django.field(
		prefetch_related = ["media"]
	)


__all__ = [
	"MonthsEnum",
	"CalendarOrder",
	"School",
	"News",
	"Calendar",
	"SettingFormat",
	"SocialMedia",
	"Coordinate",
	"Infraestructure",
	"Download",
	"Repository"
]
