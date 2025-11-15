from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import (
	create_school,
	create_school_staff,
	bulk_create_school_staff
)
from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data


def get_list_create_staff(school_id, **query):
	return reverse(
		"management:staff-list-create",
		kwargs={"pk": school_id},
		**query
	)

def get_detail_staff(id):
	return reverse(
		"management:staff-detail",
		kwargs={"pk": id}
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


class StaffListAPITest(testcases.StaffTestCase):
	def setUp(self):
		super().setUp()

		self.URL_STAFF_LIST = get_list_create_staff(
			school_id = self.school.id
		)

		bulk_create_school_staff(school = self.school, size = 10)


	def test_get_staff(self):
		"""
			Validar "GET /staff"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_staff = models.SchoolStaff.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_STAFF_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_staff)

	def test_get_staff_filter_by_name(self):
		"""
			Validar "GET /staff" filtrado por 'nombre'
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		search_name = faker.first_name()
		school_staff = [
			models.SchoolStaff(
				school_id = self.school.id,
				name = f"{search_name} {faker.last_name()}"
			) 
			for _ in range(2)
		]

		models.SchoolStaff.objects.bulk_create(school_staff)

		total_staff = models.SchoolStaff.objects.filter(
			school_id = self.school.id,
			name__icontains = search_name
		).count()

		response = self.client.get(
			get_list_create_staff(
				school_id = self.school.id,
				query = {"name": search_name}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_staff)

	def test_get_staff_filter_by_occupation(self):
		"""
			Validar "GET /staff" filtrado por 'ocupación'
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		occupation_teacher = models.OccupationStaff.teacher.value
		occupation_administrative = models.OccupationStaff.administrative.value

		total_staff_tearcher = models.SchoolStaff.objects.filter(
			school_id = self.school.id,
			occupation = occupation_teacher
		).count()
		total_staff_administrative = models.SchoolStaff.objects.filter(
			school_id = self.school.id,
			occupation = occupation_administrative
		).count()

		response = self.client.get(
			get_list_create_staff(
				school_id = self.school.id,
				query = {"occupation": occupation_teacher}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["count"], 
			total_staff_tearcher
		)

		response = self.client.get(
			get_list_create_staff(
				school_id = self.school.id,
				query = {"occupation": occupation_administrative}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code
		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["count"], 
			total_staff_administrative
		)

	def test_get_staff_without_school_permission(self):
		"""
			Generar [Error 403] "GET /staff" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_list_create_staff(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatus= response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_staff_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /staff" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_STAFF_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_staff_without_authentication(self):
		"""
			Generar [Error 403] "GET /staff" sin autenticación 
		"""

		response = self.client.get(self.URL_STAFF_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class StaffDetailAPITest(testcases.StaffDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.staff = create_school_staff(school = self.school)

		self.URL_STAFF_DETAIL = get_detail_staff(id = self.staff.id)

	def test_detail_staff(self):
		"""
			Validar "GET /staff/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_STAFF_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.staff.id)
		self.assertEqual(responseJson["name"], self.staff.name)
		self.assertEqual(responseJson["occupation"], self.staff.occupation)

	def test_detail_staff_without_school_permission(self):
		"""
			Generar [Error 403] "GET /staff/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_schoolstaff = create_school_staff()

		response = self.client.get(
			get_detail_staff(id = other_schoolstaff.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_staff_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /staff/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_STAFF_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_staff_without_authentication(self):
		"""
			Generar [Error 401] "GET /staff/:id" sin autenticación
		"""

		response = self.client.get(self.URL_STAFF_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class StaffDeleteAPITest(testcases.StaffDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.staff = create_school_staff(school = self.school)

		self.URL_STAFF_DELETE = get_detail_staff(id = self.staff.id)

	def test_delete_staff(self):
		"""
			Validar "DELETE /staff/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_STAFF_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_staff_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /staff/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		other_schoolstaff = create_school_staff()

		response = self.client.delete(
			get_detail_staff(id = other_schoolstaff.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_staff_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /staff/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_STAFF_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_staff_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /staff/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_schoolstaff"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_STAFF_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_staff_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /staff/:id" sin autenticación
		"""
		response = self.client.delete(self.URL_STAFF_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class StaffUpdateAPITest(testcases.StaffDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.staff = create_school_staff(school = self.school)

		self.URL_STAFF_UPDATE = get_detail_staff(id = self.staff.id)

		self.update_staff = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_SCHOOSTAFF_NAME),
			"occupation": faker.random_element(
				elements = models.OccupationStaff.values
			)
		}

		self.update_partial_staff = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_SCHOOSTAFF_NAME)
		}

	def test_update_staff(self):
		"""
			Validar "PUT/PATCH /staff/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.put(self.URL_STAFF_UPDATE, self.update_staff)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.staff.id)
		self.assertNotEqual(responseJson["name"], self.staff.name)
		self.assertEqual(responseJson["name"], self.update_staff["name"])
		self.assertEqual(responseJson["occupation"], self.update_staff["occupation"])

		response = self.client.patch(self.URL_STAFF_UPDATE, self.update_partial_staff)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.staff.id)
		self.assertNotEqual(responseJson["name"], self.staff.name)
		self.assertEqual(responseJson["name"], self.update_partial_staff["name"])

	def test_update_staff_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /staff/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_case = testcases_data.CREATE_STAFF_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.patch(self.URL_STAFF_UPDATE, case)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_update_staff_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /staff/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		other_schoolstaff = create_school_staff()

		response = self.client.patch(
			get_detail_staff(id = other_schoolstaff.id), 
			self.update_partial_staff
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_staff_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /staff/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.patch(self.URL_STAFF_UPDATE, self.update_partial_staff)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_staff_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /staff/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_schoolstaff"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.patch(self.URL_STAFF_UPDATE, self.update_partial_staff)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_staff_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /staff/:id" sin autenticación
		"""
		response = self.client.patch(self.URL_STAFF_UPDATE, self.update_partial_staff)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
