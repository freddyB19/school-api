import datetime

from django.utils import timezone

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


def get_create_list_calendar_url(school_id, **extra):
	return reverse(
		"management:calendar-list-create",
		kwargs = {"pk": school_id},
		**extra
	)

def get_detail_calendar_url(id):
	return reverse(
		"management:calendar-detail",
		kwargs = {"pk": id}
	)


class CalendarCreateAPITest(testcases.CalendarCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_CALENDAR_CREATE = get_create_list_calendar_url(
			school_id = self.school.id
		)
		self.add_calendar = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CALENDAR_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year()
		}


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
			get_create_list_calendar_url(school_id = other_school.id),
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


class CalendarListAPITest(testcases.CalendarTestCase):
	def setUp(self):
		super().setUp()
		
		self.URL_CALENDAR_LIST = get_create_list_calendar_url(
			school_id = self.school.id
		)

		bulk_create_calendar(
			size = 20, 
			school = self.school
		)
		bulk_create_calendar(
			size = 7, 
			school = self.school, 
			date = self.create_date()
		)

	def create_date(self, input_month:int = None):
		local_time = timezone.localtime()
		month = local_time.month if not input_month else input_month
		year = local_time.year
		
		current_date = datetime.date(
			year, month, faker.random_int(min = 1, max = 25)
		)

		return current_date


	def test_get_calendar(self):
		"""
			Validar "GET /calendar"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__year= timezone.localtime().year
		).count()

		response = self.client.get(self.URL_CALENDAR_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_calendar)


	def test_get_calendar_filter_by_month(self):
		"""
			Validar "GET /calendar?month=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		month = faker.random_int(min = 1, max = 12)

		date = self.create_date(input_month = month)

		bulk_create_calendar(size = 3, school = self.school, date = date)

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = month
		).count()

		response = self.client.get(
			get_create_list_calendar_url(
				school_id = self.school.id,
				query = {"month": month}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_calendar)

	def test_get_calendar_filter_by_title(self):
		"""
			Validar "GET /calendar?title=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		title = faker.text(max_nb_chars = models.MAX_LENGTH_CALENDAR_TITLE)

		bulk_create_calendar(
			size = 2, 
			school = self.school,
			 title = title
		)

		len_title = len(title)
		title__icontains = title[: int(len_title / 2) ]

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id,
			title__icontains = title__icontains
		).count()

		response = self.client.get(
			get_create_list_calendar_url(
				school_id = self.school.id,
				query = {"title": title__icontains}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_calendar)

	def test_get_calendar_without_school_permission(self):
		"""
			Generar [Error 403] "GET /calendar" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_create_list_calendar_url(
				school_id = other_school.id,
			)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_calendar_without_authentication(self):
		"""
			Generar [Error 401] "GET /calendar" sin autenticación
		"""
		response = self.client.get(self.URL_CALENDAR_LIST)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CalendarDetailAPITest(testcases.CalendarDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.calendar = create_calendar(school = self.school)

		self.URL_CALENDAR_DETAIL = get_detail_calendar_url(id = self.calendar.id)

	def test_detail_calendar(self):
		"""
			Validar "GET /calendar/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_CALENDAR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.calendar.id)
		self.assertEqual(responseJson["title"], self.calendar.title)
		self.assertEqual(responseJson["description"], self.calendar.description)
		self.assertEqual(responseJson["date"], self.calendar.date.strftime("%Y-%m-%d"))


	def test_detail_calendar_without_school_permission(self):
		"""
			Generar [Error 403] "GET /calendar/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_calendar = create_calendar(school = create_school())

		response = self.client.get(
			get_detail_calendar_url( id = other_calendar.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_detail_calendar_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /calendar/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_CALENDAR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_detail_calendar_without_authentication(self):
		"""
			Generar [Error 403] "GET /calendar/:id" sin autenticación
		"""

		response = self.client.get(self.URL_CALENDAR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)