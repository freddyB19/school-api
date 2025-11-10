from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import (
	create_school, 
	create_coordinate, 
	bulk_create_coordinate
)
from tests.user.utils import create_user, get_permissions
from .utils import testcases, testcases_data


def get_create_list_coordinate_url(school_id):
	return reverse(
		"management:coordinate-list-create",
		kwargs = {"pk": school_id}
	)


def get_detail_coordinate_url(id):
	return reverse(
		"management:coordinate-detail",
		kwargs = {"pk": id}
	)


class CoordinateCreateAPITest(testcases.CoordianteCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_COORDIANTE_CREATE = get_create_list_coordinate_url(
			school_id = self.school.id
		)

		coordinate = faker.local_latlng(country_code = 'VE')

		self.add_coordinate = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_COORDINATE_TITLE),
			"latitude": coordinate[0],
			"longitude": coordinate[1]
		}


	def test_create_coordiante(self):
		"""
			Validar "POST /coordiante"
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_COORDIANTE_CREATE,
			self.add_coordinate
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson["title"], self.add_coordinate["title"])
		self.assertEqual(responseJson["latitude"], self.add_coordinate["latitude"])
		self.assertEqual(responseJson["longitude"], self.add_coordinate["longitude"])


	def test_create_coordiante_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /coordiante" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_case = testcases_data.CREATE_COORDINATE_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.post(
					self.URL_COORDIANTE_CREATE,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)

	def test_create_coordiante_with_data_already_exist(self):
		"""
			Generar [Error 400] "POST /coordiante" por enviar datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		coordinate = create_coordinate(school = self.school)

		self.add_coordinate.update({
			"title": coordinate.title,
			"latitude": coordinate.latitude,
			"longitude": coordinate.longitude
		})

		response = self.client.post(
			self.URL_COORDIANTE_CREATE,
			self.add_coordinate
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_create_coordiante_without_school_permission(self):
		"""
			Generar [Error 403] "POST /coordiante" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			get_create_list_coordinate_url(school_id = other_school.id),
			self.add_coordinate
		)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_coordiante_without_user_permission(self):
		"""
			Generar [Error 403] "POST /coordiante" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_COORDIANTE_CREATE,
			self.add_coordinate
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_coordiante_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /coordiante" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(get_permissions(codenames = "add_coordinate"))

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_COORDIANTE_CREATE,
			self.add_coordinate
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_coordiante_without_authentication(self):
		"""
			Generar [Error 401] "POST /coordiante" sin autenticación
		"""
		response = self.client.post(
			self.URL_COORDIANTE_CREATE,
			self.add_coordinate
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CoordinateListAPITest(testcases.CoordinateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_COORDIANTE_LIST = get_create_list_coordinate_url(
			school_id = self.school.id
		)

		bulk_create_coordinate(school = self.school, size = 10)


	def test_get_coordiante(self):
		"""
			Validar "GET /coordiante"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_coordinate = models.Coordinate.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_COORDIANTE_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_coordinate)


	def test_get_coordiante_without_school_permission(self):
		"""
			Generar [Error 403] "GET /coordiante" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_create_list_coordinate_url(
				school_id = other_school.id
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_coordiante_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /coordiante" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_COORDIANTE_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_coordiante_without_authentication(self):
		"""
			Generar [Error 401] "GET /coordiante" sin autenticación
		"""
		response = self.client.get(self.URL_COORDIANTE_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CoordinateDetailAPITest(testcases.CoordianteDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.coordinate = create_coordinate(school = self.school)

		self.URL_COORDIANTE_DETAIL = get_detail_coordinate_url(
			id = self.coordinate.id
		)


	def test_detail_coordinate(self):
		"""
			Validar "GET /coordinate/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_COORDIANTE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.coordinate.id)
		self.assertEqual(responseJson["title"], self.coordinate.title)
		self.assertEqual(responseJson["latitude"], self.coordinate.latitude)
		self.assertEqual(responseJson["longitude"], self.coordinate.longitude)


	def test_detail_coordinate_without_school_permission(self):
		"""
			Generar [Error 403] "GET /coordinate/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_coordinate = create_coordinate()

		response = self.client.get(
			get_detail_coordinate_url(id = other_coordinate.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_coordinate_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /coordinate/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_COORDIANTE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_coordinate_without_authetication(self):
		"""
			Generar [Error 401] "GET /coordinate/:id" sin autenticación
		"""
		response = self.client.get(self.URL_COORDIANTE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CoordinateDeleteAPITest(testcases.CoordianteDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.coordinate = create_coordinate(school = self.school)

		self.URL_COORDIANTE_DELETE = get_detail_coordinate_url(
			id = self.coordinate.id
		)

	def test_delete_coordinate(self):
		"""
			Validar "DELETE /coordinate/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_COORDIANTE_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_coordinate_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /coordinate/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		coordinate = create_coordinate()

		response = self.client.delete(
			get_detail_coordinate_url(id = coordinate.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_coordinate_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /coordinate/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_COORDIANTE_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_coordinate_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /coordinate/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_coordinate"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_COORDIANTE_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_coordinate_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /coordinate/:id" sin autenticación
		"""
		response = self.client.get(self.URL_COORDIANTE_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)