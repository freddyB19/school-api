import json, pprint, datetime

from django.utils import timezone

from apps.graphql.school.types import Months
from apps.school import models

from tests import faker
from tests.school.utils import bulk_create_calendar, create_calendar

from .utils import testcases


class SchoolQueryBySubdomainTest(testcases.SchoolQuerySubdomainTestCase):

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

		self.assertTrue(school["settings"])
		self.assertTrue(school["news"])
		self.assertTrue(school["networks"])
		self.assertTrue(school["coordinates"])


	def test_get_schoolBySubdomain_with_wrong_subdomain(self):
		"""
			Obtener un error por 'subdomain' invalida
		"""

		self.variables_schoolBySubdomain.update({"subdomain": faker.slug()})

		result = self.query(
			self.query_schoolBySubdomain,
			variables = self.variables_schoolBySubdomain
		)

		responseJson = result.json()
		responseStatusCode = result.status_code
		
		self.assertEqual(responseStatusCode, 200)
		
		school = responseJson["data"]["schoolBySubdomain"]

		self.assertIsNone(school["school"])
		self.assertIsNone(school["settings"])
		self.assertIsNone(school["networks"])
		self.assertIsNone(school["news"])
		self.assertIsNone(school["coordinates"])

class SchoolQuerySchoolService(testcases.SchoolQueryServicesTestCase):
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

		self.assertTrue(serviceOnline["downloads"])
		self.assertTrue(serviceOnline["repositories"])
		self.assertTrue(serviceOffline["infraestructures"])



class SchoolQuerySchoolCalendar(testcases.SchoolQueryCalendarTestCase):
	def setUp(self):
		super().setUp()
		bulk_create_calendar(
			size = 20,
			school = self.school,
		)

		self.current_date = timezone.localtime()
		self.variables_schoolCalendar = {
			"subdomain": self.school.subdomain,
			"month": Months.get(self.current_date.month).name,
		}

	def test_get_schoolCalendar(self):
		"""
			Fechas del calendario de una escuela
		"""
		for _ in range(30):
			create_calendar(school = self.school, date = faker.date_this_month())

		other_date = faker.date_between(start_date = "-2y", end_date = "-1y")
		bulk_create_calendar(
			size = 5, 
			school = self.school,
			date = datetime.date(
				other_date.year,
				self.current_date.month,
				other_date.day
			)
		)
		
		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = self.current_date.month,
			date__year = self.current_date.year
		).count()


		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		responseJson = result.json()
		resposeStatusCode = result.status_code

		self.assertEqual(resposeStatusCode, 200)

		calendar = responseJson["data"]["schoolCalendar"]

		self.assertTrue(calendar["edges"])
		self.assertEqual(len(calendar["edges"]), total_calendar)

	def test_get_schoolCalendar_filter_by_month(self):
		"""
			Obtener fechas del calendario, definiendo parámetro de búsqueda [month] 
		"""
		current_year = self.current_date.year
		for month in range(1, 13):
			calendars = bulk_create_calendar(
				size = faker.random_int(min = 10, max = 20), 
				school = self.school,
				date = datetime.date(
					current_year, 
					month, 
					faker.random_int(min = 1, max = 26)
				)
			)

		search_month = faker.random_int(min = 1, max = 12)
		self.variables_schoolCalendar.update({"month": Months.get(search_month).name})

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = search_month,
			date__year = current_year
		).count()

		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		responseJson = result.json()
		resposeStatusCode = result.status_code

		self.assertEqual(resposeStatusCode, 200)

		calendar = responseJson["data"]["schoolCalendar"]

		self.assertEqual(len(calendar["edges"]), total_calendar)

	def test_get_schoolCalendar_with_wrong_subdomain(self):
		"""
			Obtener fechas del calendario de una escuela, pero enviando un 'subdomain' incorrecto
		"""
		self.variables_schoolCalendar.update({"subdomain": faker.slug()})

		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		responseJson = result.json()
		resposeStatusCode = result.status_code

		self.assertEqual(resposeStatusCode, 200)

		calendar = responseJson["data"]["schoolCalendar"]

		self.assertFalse(calendar["edges"])


	def test_get_schoolCalendar_current_month(self):
		"""
			Obtener fechas del calendario del mes actual de una escuela
			- Sin definir parámetro de búsqueda: [month]
		"""
		self.variables_schoolCalendar.pop("month")

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = self.current_date.month,
			date__year = self.current_date.year
		).count()

		result = self.query(
			self.query_schoolCalendar,
			variables = self.variables_schoolCalendar
		)

		responseJson = result.json()
		resposeStatusCode = result.status_code

		self.assertEqual(resposeStatusCode, 200)

		calendar = responseJson["data"]["schoolCalendar"]

		self.assertTrue(calendar["edges"])
		self.assertEqual(len(calendar["edges"]), total_calendar)
