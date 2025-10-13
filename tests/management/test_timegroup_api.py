from django.urls import reverse

from .utils import testcases

from apps.school import models

from tests import faker

from .utils import testcases_data
from tests.school.utils import create_time_group


def get_detail_timegroup_url(id):
	return reverse(
		"management:timegroup-detail",
		kwargs={"pk": id}
	)


class  TimeGroupDetailAPITest(testcases.TimeGroupDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()
		
		self.time_group = create_time_group()

		self.URL_TIMEGROUP_DETAIL = get_detail_timegroup_url(
			id = self.time_group.id
		)

	def test_detail_timegroup(self):
		"""
			Validar "GET /officehour/time/:id"
		"""

		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_TIMEGROUP_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.time_group.id)


	def test_detail_timegroup_does_not_exist(self):
		"""
			Generar [Error 404] "GET /officehour/time/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		wrong_id = faker.random_int(min = self.time_group.id + 1)
		
		response = self.client.get(
			get_detail_timegroup_url(
				id = wrong_id
			)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)



class TimeGroupUpdateAPITest(testcases.TimeGroupDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()
		
		self.time_group = create_time_group()

		self.URL_TIMEGROUP_DETAIL = get_detail_timegroup_url(
			id = self.time_group.id
		)

	def test_update_timegroup(self):
		"""
			Validar "PUT/PATCH /officehour/time/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		update = {
			"type": faker.text(max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE - 1)
		}

		response = self.client.patch(
			self.URL_TIMEGROUP_DETAIL,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.time_group.id)


	def test_update_timegroup_with_does_not_exist(self):
		"""
			Generar [Error 404] "PUT/PATCH /officehour/time/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		update = {
			"type": faker.text(max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE - 1)
		}

		wrong_id = faker.random_int(min = self.time_group.id + 1)

		response = self.client.patch(
			get_detail_timegroup_url(id = wrong_id),
			update
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_update_timegroup_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /officehour/time/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_cases = testcases_data.UPDATE_TIMEGROUP_WITH_WRONG_DATA


		for case in  test_cases:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_TIMEGROUP_DETAIL,
					case['update']
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_update_timegroup_without_user_permission(self):
		"""
			Generar [Error 400] "PUT/PATCH /officehour/time/:id" por usuario sin permisos
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		update = {
			"type": faker.text(max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE - 1)
		}

		response = self.client.patch(
			self.URL_TIMEGROUP_DETAIL,
			update
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_timegroup_without_authentication(self):
		"""
			Generar [Error 400] "PUT/PATCH /officehour/time/:id" sin autenticación
		"""
		
		update = {
			"type": faker.text(max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE - 1)
		}

		response = self.client.patch(
			self.URL_TIMEGROUP_DETAIL,
			update
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class TimeGroupDeleteAPITest(testcases.TimeGroupDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()
		
		self.time_group = create_time_group()

		self.URL_TIMEGROUP_DETAIL = get_detail_timegroup_url(
			id = self.time_group.id
		)

	def test_delete_timegroup(self):
		"""
			Validar "DELETE /officehour/time/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(
			self.URL_TIMEGROUP_DETAIL
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_timegroup_with_does_not_exist(self):
		"""
			Generar [Error 404] "DELETE /officehour/time/:id" por que no existe
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)
		
		wrong_id = faker.random_int(min = self.time_group.id + 1)

		response = self.client.delete(
			get_detail_timegroup_url(id = wrong_id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_delete_timegroup_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /officehour/time/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)
		
		wrong_id = faker.random_int(min = self.time_group.id + 1)

		response = self.client.delete(
			get_detail_timegroup_url(id = wrong_id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_delete_timegroup_without_authetication(self):
		"""
			Generar [Error 403] "DELETE /officehour/time/:id" sin autenticación
		"""
		response = self.client.delete(
			self.URL_TIMEGROUP_DETAIL
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
