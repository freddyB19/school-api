import json
 
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