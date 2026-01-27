from django.test import TestCase
from django.utils import timezone

from strawberry_django.test.client import TestClient

from apps.graphql.school.types import MonthsEnum

from tests.school.utils import utils

from .schemas import (
	QUERY_SCHOOL, 
	QUERY_SCHOOL_CALENDAR
)

URL = "/graphql"

class SchoolQueryTestCase(TestCase):
	def setUp(self):
		self.client = TestClient(URL)
		self.school = utils.create_school()


class SchoolQueryHomeTestCase(SchoolQueryTestCase):
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

		self.query = QUERY_SCHOOL

		self.variables = {
			"subdomain": self.school.subdomain
		}


class SchoolQueryCalendarTestCase(SchoolQueryTestCase):
	def setUp(self):
		super().setUp()

		utils.bulk_create_calendar(
			size = 10,
			school = self.school,
		)

		self.current_date = timezone.localtime()

		self.query = QUERY_SCHOOL_CALENDAR
		self.variables = {
			"subdomain": self.school.subdomain,
			"month": MonthsEnum(self.current_date.month).name,
		}
