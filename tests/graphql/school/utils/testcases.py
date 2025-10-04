from django.utils import timezone

from graphene_django.utils.testing import GraphQLTestCase

from apps.graphql.school.types import Months

from tests.school.utils import utils

from .schemas import (
	QUERY_SCHOOL_SERVICE,
	QUERY_SCHOOL_CALENDAR,
	QUERY_SCHOOL_BY_SUBDOMAIN
)

class SchoolQueryTestCase(GraphQLTestCase):
	def setUp(self):
		self.school = utils.create_school()


class SchoolQuerySubdomainTestCase(SchoolQueryTestCase):
	def setUp(self):
		super().setUp()

		self.school.setting.colors.set(
			utils.bulk_create_color_hex_format(size = 5)
		)

		utils.bulk_create_social_media(
			size = 3,
			school = self.school
		)
		utils.bulk_create_news(
			size = 10,
			school = self.school, 
			status="publicado"
		)
		utils.bulk_create_coordinate(
			size = 10,
			school = self.school
		)
		self.query_schoolBySubdomain = QUERY_SCHOOL_BY_SUBDOMAIN

		self.variables_schoolBySubdomain = {
			"subdomain": self.school.subdomain
		}


class SchoolQueryCalendarTestCase(SchoolQueryTestCase):
	def setUp(self):
		super().setUp()
		self.current_date = timezone.localtime()

		total_create_current_date = 5
		
		utils.bulk_create_calendar(
			size = total_create_current_date,
			school = self.school, 
			date = self.current_date
		)
		utils.bulk_create_calendar(
			size = 3,
			school = self.school,
		)

		self.query_schoolCalendar = QUERY_SCHOOL_CALENDAR
		self.variables_schoolCalendar = {
			"subdomain": self.school.subdomain,
			"month": Months.get(self.current_date.month).name,
		}


class SchoolQueryServicesTestCase(SchoolQueryTestCase):
	def setUp(self):
		super().setUp()

		utils.bulk_create_repository(
			size = 15,
			school = self.school
		)
		utils.bulk_create_infraestructure(
			size = 15,
			school = self.school
		)
		utils.bulk_create_download(
			size = 15,
			school = self.school
		)

		self.query_schoolService = QUERY_SCHOOL_SERVICE
		self.variables_schoolService = {
			"schoolId": self.school.id
		}