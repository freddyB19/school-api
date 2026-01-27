from django.utils import timezone

import strawberry, strawberry_django
from strawberry_django.relay import DjangoListConnection
from strawberry_django.pagination import OffsetPaginated

from apps.school import models

from .types import (
	MonthsEnum,
	School,
	News,
	Calendar,
	CalendarOrder,
	SettingFormat,
	SocialMedia,
	Coordinate,
	Infraestructure,
	Download,
	Repository
)


@strawberry.type
class SchoolQuery:
	settings: list[SettingFormat] = strawberry_django.field()
	socialmedia: list[SocialMedia] = strawberry_django.field(pagination=True)
	news: DjangoListConnection[News] = strawberry_django.connection()
	download: DjangoListConnection[Download] = strawberry_django.connection()
	coordinate: DjangoListConnection[Coordinate] = strawberry_django.connection()
	repository: DjangoListConnection[Repository] = strawberry_django.connection()
	infraestructure: DjangoListConnection[Infraestructure] = strawberry_django.connection()

	@strawberry_django.field
	def school(self, subdomain: str) -> School | None:
		return models.School.objects.filter(subdomain = subdomain).first()

	@strawberry_django.offset_paginated(OffsetPaginated[Calendar], order = CalendarOrder)
	def calendar(self, subdomain: str, month: MonthsEnum = None) -> list[Calendar] | None:
		
		current_time = timezone.localtime()

		search_month = month if month else current_time.month

		calendar = models.Calendar.objects.filter(
			school__subdomain = subdomain,
			date__month = search_month,
			date__year = current_time.year
		)

		return calendar
