import random

from django.urls import reverse

from . import faker

from apps.school import models
from apps.school.tests.utils.utils import create_school

from apps.user.tests.utils.utils import create_user

from .utils.utils import set_time, set_daysweek
from .utils.testcases import OfficeHourCreateTest

class OfficeHourCreateAPITest(OfficeHourCreateTest):
	def setUp(self):
		super().setUp()

		self.URL_OFFICEHOUR = self.get_school_officehour_url(
			school_id = self.school.id
		)

		# Los dias de la semana se representan mediante números L = 1, ... V = 5
		self.daysweek = set_daysweek()
		
		self.create_officehour = {
			"description": faker.text(max_nb_chars = 50),
			"time_group": {
				"type": faker.text(max_nb_chars = 30),
				"daysweek": self.daysweek,
				"opening_time": set_time(hour = 6, minute = 30),
				"closing_time": set_time(hour = 16, minute = 30),
				"active": random.choice([True, False]),
				"overview": faker.paragraph()
			}
		}


	def get_school_officehour_url(self, school_id):
		return reverse(
			"management:officehour-list-create",
			kwargs={"pk": school_id}
		)


	def test_create_officehour(self):
		"""
			Validar "POST /officehour"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson["school"], self.school.id)
		self.assertEqual(
			responseJson["interval_description"],
			self.create_officehour["description"]
		)
		self.assertEqual(
			responseJson["time_group"]["type"],
			self.create_officehour["time_group"]["type"]
		)
		self.assertEqual(
			responseJson["time_group"]["overview"],
			self.create_officehour["time_group"]["overview"]
		)
		self.assertEqual(
			responseJson["time_group"]["active"],
			self.create_officehour["time_group"]["active"]
		)
		self.assertTrue(responseJson["time_group"]["daysweek"])


	def test_create_officehour_without_dasyweek(self):
		"""
			Validar "POST /officehour" sin enviar 'daysweek'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)
		
		self.create_officehour["time_group"].pop("daysweek")

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertFalse(responseJson["time_group"]["daysweek"])
		self.assertEqual(responseJson["school"], self.school.id)
		self.assertEqual(
			responseJson["interval_description"],
			self.create_officehour["description"]
		)
		self.assertEqual(
			responseJson["time_group"]["type"],
			self.create_officehour["time_group"]["type"]
		)
		self.assertEqual(
			responseJson["time_group"]["overview"],
			self.create_officehour["time_group"]["overview"]
		)

	def test_create_officehour_without_active(self):
		"""
			Validar "POST /officehour" sin enviar 'active'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.create_officehour["time_group"].pop("active")

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertTrue(responseJson["time_group"]["active"])
		self.assertEqual(responseJson["school"], self.school.id)
		self.assertEqual(
			responseJson["interval_description"],
			self.create_officehour["description"]
		)
		self.assertEqual(
			responseJson["time_group"]["type"],
			self.create_officehour["time_group"]["type"]
		)
		self.assertEqual(
			responseJson["time_group"]["overview"],
			self.create_officehour["time_group"]["overview"]
		)
		self.assertTrue(responseJson["time_group"]["daysweek"])


	def test_create_officehour_without_overview(self):
		"""
			Validar "POST /officehour" sin enviar 'overview'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.create_officehour["time_group"].pop("overview")

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertIsNone(responseJson["time_group"]["overview"])
		self.assertEqual(responseJson["school"], self.school.id)
		self.assertEqual(
			responseJson["interval_description"],
			self.create_officehour["description"]
		)
		self.assertTrue(
			responseJson["time_group"]["daysweek"]
		)
		self.assertEqual(
			responseJson["time_group"]["active"],
			self.create_officehour["time_group"]["active"]
		)


	def test_create_officehour_with_wrong_description(self):
		"""
			Generar [Error 400] "POST /officehour" por enviar un valor muy corto (o largo) en 'description' 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_cases = [
			{
				"description": faker.pystr(
					max_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D + 1
				)
			},
			{
				"description": faker.pystr(
					max_chars = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D - 1
				)
			}
		]

		for case in test_cases:
			with self.subTest(case  = case):
				self.create_officehour.update({
					"description": case["description"]
				})

				response = self.client.post(
					self.URL_OFFICEHOUR,
					self.create_officehour
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_create_officehour_with_wrong_type(self):
		"""
			Generar [Error 400] "POST /officehour" por enviar un valor muy corto (o largo) en 'type' 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)
		
		test_cases = [
			{
				"type": faker.pystr(
					max_chars = models.MAX_LENGTH_TYPEGROUP_TYPE + 1
				)
			},
			{
				"type": faker.pystr(
					max_chars = models.MIN_LENGTH_TYPEGROUP_TYPE - 1
				)
			}
		]

		for case in test_cases:
			with self.subTest(case  = case):
				self.create_officehour["time_group"].update({
					"type": case["type"]
				})

				response = self.client.post(
					self.URL_OFFICEHOUR,
					self.create_officehour
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_create_officehour_with_wrong_time(self):
		"""
			Generar [Error 400] "POST /officehour" por enviar 'closing_time' <= 'opening_time' 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.create_officehour["time_group"].update({
			"closing_time": set_time(hour = 6, minute = 30),
			"opening_time": set_time(hour = 15, minute = 30),
		})

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseStatus = response.status_code
		self.assertEqual(responseStatus, 400)


	def test_create_officehour_with_wrong_daysweek(self):
		"""
			Generar [Error 400] "POST /officehour" por valores incorrectos en 'daysweek' 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.create_officehour["time_group"].update({
			"daysweek": set_daysweek(days = [9,1,6,7,8,3])
		})

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)


	def test_create_officehour_without_user_permission(self):
		"""
			Generar [Error 403] "POST /officehour" por usuarios sin permisos para crear este recurso
		"""

		test_cases = [
			{"user": self.user_with_delete_perm},
			{"user": self.user_with_view_perm}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = case["user"])

				response = self.client.post(
					self.URL_OFFICEHOUR,
					self.create_officehour
				)

				responseStatus = response.status_code
				
				self.assertEqual(responseStatus, 403)


	def test_create_officehour_without_school_permision(self):
		"""
			Generar [Error 403] "POST /officehour" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			self.get_school_officehour_url(school_id = other_school.id),
			self.create_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_create_officehour_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /officehour" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user(role = 0)

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_officehour_without_authentication(self):
		"""
			Generar [Error 401] en "POST /officehour" no autenticarse
		"""
		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

