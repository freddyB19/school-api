from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import (
	create_school,
	create_calendar,
	bulk_create_calendar
)
from tests.user.utils import create_user

from .utils import testcases, testcases_data


class CalendarCreateAPITest(testcases.CalendarCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_CALENDAR_CREATE = self.get_create_calendar_url(
			school_id = self.school.id
		)
		self.add_calendar = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CALENDAR_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year()
		}

	def get_create_calendar_url(self, school_id):
		return reverse(
			"management:calendar-list-create",
			kwargs = {"pk": school_id}
		)


	def test_create_calendar(self):
		"""
			Validar "POST /calendar"
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_CALENDAR_CREATE,
			self.add_calendar
		)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 201)
		self.assertTrue(responseJson["id"])
		self.assertEqual(responseJson["title"], self.add_calendar["title"])
		self.assertEqual(responseJson["description"], self.add_calendar["description"])

	def test_create_calendar_without_description(self):
		"""
			Validar "POST /calendar" sin enviar descripción
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.add_calendar.pop("description")

		response = self.client.post(
			self.URL_CALENDAR_CREATE,
			self.add_calendar
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertTrue(responseJson["id"])
		self.assertEqual(responseJson["title"], self.add_calendar["title"])
		self.assertIsNone(responseJson["description"])

	def test_create_calendar_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /calendar" por enviar datos invalidos
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		test_cases = testcases_data.CREATE_CALENDAR_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):

				response = self.client.post(
					self.URL_CALENDAR_CREATE,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)

	def test_create_calendar_without_school_permisson(self):
		"""
			Generar [Error 403] "POST /calendar" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)


		other_school = create_school()

		response = self.client.post(
			self.get_create_calendar_url(school_id = other_school.id),
			self.add_calendar
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_calendar_without_user_permission(self):
		"""
			Generar [Error 403] "POST /calendar" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_CALENDAR_CREATE,
			self.add_calendar
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_calendar_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /calendar" por usuario que no pertenece a la administración de la escuela
		"""

		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_CALENDAR_CREATE,
			self.add_calendar
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_calendar_without_authentication(self):
		"""
			Generar [Error 401] "POST /calendar" usuario sin autenticar
		"""
		response = self.client.post(
			self.URL_CALENDAR_CREATE,
			self.add_calendar
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)