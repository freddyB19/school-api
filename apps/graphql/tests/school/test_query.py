import json, datetime

from graphene_django.utils.testing import GraphQLTestCase

from apps.school.tests.utils.utils import (
	create_school,
	create_color_hex_format,
	create_calendar,
	create_social_media,
	create_coordinate,
	create_grade,
	create_repository,
	create_infraestructure,
	create_download,
	create_news,
)

from apps.graphql.school.types import Months

from .utils.schemas import (
	QUERY_SCHOOL_SERVICE,
	QUERY_SCHOOL_CALENDAR,
	QUERY_SCHOOL_BY_SUBDOMAIN
)

class SchoolQueryTest(GraphQLTestCase):
	def setUp(self):
		self.current_date = datetime.datetime.utcnow()

		self.school = create_school()
		self.school.setting.colors.set(create_color_hex_format())
	
		settings = self.school.setting
		self.settings_colors = [data.color for data in settings.colors.all()]

		self.calendar = create_calendar(id = self.school.id, date = self.current_date)
		self.networks = create_social_media(id = self.school.id)
		self.news = create_news(id = self.school.id, status="publicado")
		self.coordinate = create_coordinate(id = self.school.id)
		self.repository = create_repository(id = self.school.id)
		self.infra = create_infraestructure(id = self.school.id)
		self.downloads = create_download(id = self.school.id)

		self.query_schoolBySubdomain = QUERY_SCHOOL_BY_SUBDOMAIN

		self.variables_schoolBySubdomain = {
			"subdomain": self.school.subdomain
		}

		self.query_schoolService = QUERY_SCHOOL_SERVICE
		self.variables_schoolService = {
			"schoolId": self.school.id
		}

		self.query_schoolCalendar = QUERY_SCHOOL_CALENDAR
		self.variables_schoolCalendar = {
			"subdomain": self.school.subdomain,
			"month": Months.get(self.current_date.month).name,
			"first": 2 
		}


	def test_get_schoolBySubdomain(self):
		"""
			Obtener la información de una escuela por su 'subdomain'
		"""
		result = self.query(
			self.query_schoolBySubdomain,
			variables = self.variables_schoolBySubdomain
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		school = response["data"]["schoolBySubdomain"]

		self.assertEqual(
			school["school"]["subdomain"],
			self.school.subdomain
		)
		self.assertEqual(
			school["school"]["name"],
			self.school.name
		)

		self.assertEqual(
			school["settings"]["color"][0],
			self.settings_colors[0]
		)

		self.assertEqual(
			school["news"][0]["id"],
			str(self.news.id)
		)
		self.assertEqual(
			school["news"][0]["title"],
			self.news.title
		)

		self.assertEqual(
			school["networks"][0]["profile"],
			self.networks.profile
		)

		self.assertEqual(
			school["coordinates"][0]["id"],
			str(self.coordinate.id)
		)
		self.assertEqual(
			school["coordinates"][0]["title"],
			self.coordinate.title
		)


	def test_get_schoolService(self):
		"""
			Obtener la información de los servicios de una escuela
		"""
		result = self.query(
			self.query_schoolService,
			variables = self.variables_schoolService
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		serviceOnline = response["data"]["schoolServiceOnline"]
		serviceOffline = response["data"]["schoolServiceOffline"]

		self.assertEqual(
			serviceOnline["downloads"][0]["id"],
			str(self.downloads.id)
		)
		self.assertEqual(
			serviceOnline["downloads"][0]["title"],
			self.downloads.title
		)
		
		self.assertEqual(
			serviceOnline["repositories"][0]["id"],
			str(self.repository.id)
		)

		self.assertEqual(
			serviceOnline["repositories"][0]["project"],
			self.repository.name_project
		)

		self.assertEqual(
			serviceOffline["infraestructure"][0]["id"],
			str(self.infra.id)
		)
		self.assertEqual(
			serviceOffline["infraestructure"][0]["photo"],
			self.infra.media.first().photo
		)


	def test_get_schoolCalendar(self):
		"""
			Fechas del calendario de una escuela
		"""
		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		calendar = response["data"]["schoolCalendar"]

		self.assertTrue(calendar["edges"])
		self.assertTrue(
			calendar["edges"][0]["node"]["calendarId"], 
			self.calendar.id
		)
		self.assertTrue(
			calendar["edges"][0]["node"]["title"], 
			self.calendar.title
		)


	def test_get_schoolCalendar_with_wrong_subdomain(self):
		"""
			Obtener fechas del calendario de una escuela pero, enviando un 'subdomain' incorrecto
		"""
		self.variables_schoolCalendar.update({"subdomain": "san-carmen"})

		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		response = json.loads(result.content)

		calendar = response["data"]["schoolCalendar"]

		self.assertFalse(calendar["edges"])


	def test_get_schoolCalendar_current_month(self):
		"""
			Obtener fechas del calendario del mes actual de una escuela
		"""
		self.variables_schoolCalendar.pop("month")

		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		response = json.loads(result.content)

		calendar = response["data"]["schoolCalendar"]

		self.assertEqual(
			calendar["edges"][0]["node"]["date"],
			self.calendar.date.strftime("%Y-%m-%d")
		)

		self.assertTrue(
			calendar["edges"][0]["node"]["date"] == self.current_date.strftime("%Y-%m-%d")
		)


