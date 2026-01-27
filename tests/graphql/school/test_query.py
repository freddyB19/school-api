"""
	Estos tests cumplen la función de validar aquellas [queries]
	cuya utilidad son para el suministro de datos para la parte web 
	de las escuelas.
"""
import pprint, datetime

from apps.school import models
from apps.graphql.school.types import MonthsEnum

from tests import faker
from tests.school.utils import bulk_create_calendar, create_calendar

from .utils import testcases


class SchoolQueryHomeTest(testcases.SchoolQueryHomeTestCase):

	def test_get_school(self):
		"""
			Obtener la información de una escuela por su 'subdomain'
		"""
		result = self.client.query(
			self.query,
			variables = self.variables
		)

		self.assertIsNone(result.errors)

		response = result.data

		self.assertIn("news", response)
		self.assertIn("school", response)
		self.assertIn("settings", response)
		self.assertIn("download", response)
		self.assertIn("coordinate", response)
		self.assertIn("repository", response)
		self.assertIn("socialmedia", response)
		self.assertIn("infraestructure", response)

		self.assertEqual(response["school"]["subdomain"], self.variables["subdomain"])

		self.assertTrue(response["settings"])
		self.assertTrue(response["socialmedia"])
		self.assertTrue(response["news"]['edges'])
		self.assertTrue(response["download"]['edges'])
		self.assertTrue(response["coordinate"]['edges'])
		self.assertTrue(response["repository"]['edges'])
		self.assertTrue(response["infraestructure"]['edges'])

	def test_get_school_with_wrong_subdomain(self):
		"""
			Obtener un error por 'subdomain' invalida
		"""

		self.variables.update({"subdomain": faker.slug()})

		result = self.client.query(
			self.query,
			variables = self.variables
		)

		self.assertIsNone(result.errors)

		response = result.data
		
		self.assertIsNone(response["school"])

		self.assertNotEqual(self.variables["subdomain"], self.school.subdomain)

		self.assertFalse(response["settings"])
		self.assertFalse(response["socialmedia"])
		self.assertFalse(response["news"]['edges'])
		self.assertFalse(response["download"]['edges'])
		self.assertFalse(response["coordinate"]['edges'])
		self.assertFalse(response["repository"]['edges'])
		self.assertFalse(response["infraestructure"]['edges'])

class SchoolQuerySchoolCalendar(testcases.SchoolQueryCalendarTestCase):

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


		result = self.client.query(
			self.query,
			variables = self.variables
		)

		response = result.data

		calendar = response["calendar"]

		self.assertTrue(calendar["results"])
		self.assertEqual(calendar["totalCount"], total_calendar)

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
		self.variables.update({"month": MonthsEnum(search_month).name})

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = search_month,
			date__year = current_year
		).count()

		result = self.client.query(
			self.query,
			variables = self.variables
		)

		response = result.data

		calendar = response['calendar']

		self.assertEqual(calendar["totalCount"], total_calendar)

	def test_get_schoolCalendar_with_wrong_subdomain(self):
		"""
			Obtener fechas del calendario de una escuela, pero enviando un 'subdomain' incorrecto
		"""
		self.variables.update({"subdomain": faker.slug()})

		without_dates = 0

		result = self.client.query(
			self.query,
			variables = self.variables
		)

		response = result.data

		calendar = response["calendar"]

		self.assertEqual(calendar['totalCount'], without_dates)

	def test_get_schoolCalendar_current_month(self):
		"""
			Obtener fechas del calendario del mes actual de una escuela
			- Sin definir parámetro de búsqueda: [month]
		"""
		self.variables.pop("month")

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = self.current_date.month,
			date__year = self.current_date.year
		).count()

		result = self.client.query(
			self.query,
			variables = self.variables
		)

		response = result.data
		
		calendar = response["calendar"]

		self.assertEqual(calendar['totalCount'], total_calendar)
