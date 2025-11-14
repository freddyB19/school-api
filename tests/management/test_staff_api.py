from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import create_school
from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data


def get_list_create_staff(school_id):
	return reverse(
		"management:staff-list-create",
		kwargs={"pk": school_id}
	)


class StaffCreaetAPITest(testcases.StaffCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_STAFF_CREATE = get_list_create_staff(school_id = self.school.id)

		self.add_staff = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_SCHOOSTAFF_NAME),
			"occupation": faker.random_element(
				elements = models.OccupationStaff.values
			)
		}


	def test_create_staff(self):
		"""
			Validar "POST /staff"
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_STAFF_CREATE,
			self.add_staff
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(responseJson["name"], self.add_staff["name"])
		self.assertEqual(responseJson["occupation"], self.add_staff["occupation"])

	def test_create_staff_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /staff" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_case = testcases_data.CREATE_STAFF_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.post(
					self.URL_STAFF_CREATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

	def test_create_staff_without_school_permission(self):
		"""
			Generar [Error 403] "POST /staff" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			get_list_create_staff(school_id = other_school.id),
			self.add_staff
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_staff_without_user_permission(self):
		"""
			Generar [Error 403] "POST /staff" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_STAFF_CREATE,
			self.add_staff
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_staff_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /staff" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["add_schoolstaff"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_STAFF_CREATE,
			self.add_staff
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_staff_without_authentication(self):
		"""
			Generar [Error 401] "POST /staff" sin autenticación
		"""
		response = self.client.post(
			self.URL_STAFF_CREATE,
			self.add_staff
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)