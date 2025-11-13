import pprint
from django.urls import reverse

from .utils import testcases

from apps.school import models

from tests import faker

from .utils import testcases_data, set_daysweek, set_format_dasyweek_query
from tests.school.utils import (
	create_school,
	create_time_group,
	bulk_create_officehour,
)
from tests.user.utils import create_user


def get_detail_timegroup_url(id):
	return reverse(
		"management:timegroup-detail",
		kwargs={"pk": id}
	)

class TimeGroupListAPITest(testcases.TimeGroupTestCase):
	def setUp(self):
		super().setUp()

		bulk_create_officehour(size = 5, school = self.school)

		self.URL_TIMEGROUP_LIST = self.get_list_timegroup_url(
			school_id = self.school.id
		)

	def get_list_timegroup_url(self, school_id, **extra):
		return reverse(
			"management:timegroup-list",
			kwargs={"pk": school_id},
			**extra
		)

	def test_list_timegroup(self):
		"""
			Validar "GET school/:id/officehour/time"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_time_group = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id
		).count()

		response = self.client.get(self.URL_TIMEGROUP_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_time_group)

	def test_list_timegroup_filter_by_type(self):
		"""
			Validar "GET school/:id/officehour/time?type=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		type = faker.text(max_nb_chars = 15)

		bulk_create_officehour(
			size = 2,
			school = self.school,
			time_group = create_time_group(type = type)
		)

		type_icontains =  type[:11]

		time_group_filter_by_type = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id,
			type__icontains = type_icontains
		).count()

		response = self.client.get(
			self.get_list_timegroup_url(
				school_id = self.school.id,
				query = {"type": type_icontains}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], time_group_filter_by_type)


	def test_list_timegroup_filter_by_daysweek(self):
		"""
			Validar "GET school/:id/officehour/time?days=<...>, <...>, ..."
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		daysweek = models.DaysWeek.objects.all()
		time_group = create_time_group(daysweek = faker.random_elements(
			elements = daysweek,
			length = 2
		))

		bulk_create_officehour(
			size = 3,
			school = self.school,
			time_group = time_group
		)

		#Lista de días de la semana mediante enteros: [1-5]
		days = [day.day for day in time_group.daysweek.all()]

		time_group_filter_by_daysweek = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id,
			daysweek__day__in = days
		).distinct()

		response = self.client.get(
			self.get_list_timegroup_url(
				school_id = self.school.id,
				query = {"days": set_format_dasyweek_query(selected = days)}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], time_group_filter_by_daysweek.count())


	def test_list_timegroup_filter_by_active(self):
		"""
			Validar "GET school/:id/officehour/time?is_active=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		active = False

		bulk_create_officehour(
			size = 2,
			school = self.school,
			time_group = create_time_group(active = active)
		)

		time_group_filter_by_active = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id,
			active = active
		).count()

		response = self.client.get(
			self.get_list_timegroup_url(
				school_id = self.school.id,
				query = {"is_active": active}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], time_group_filter_by_active)


	def test_list_timegroup_without_school_permission(self):
		"""
			Generar [Error 403] "school/:id/officehour/time" por acceder a información de otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			self.get_list_timegroup_url(school_id = other_school.id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_list_timegroup_with_wrong_user(self):
		"""
			Generar [Error 403] "GET school/:id/officehour/time" por usuario que no forma parte de la administración de la escuela
		"""

		user = create_user()

		self.client.force_authenticate(user = user)

		total_time_group = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id
		).count()

		response = self.client.get(self.URL_TIMEGROUP_LIST)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_list_timegroup_without_authentication(self):
		"""
			Generar [Error 401] "school/:id/officehour/time"
		"""

		total_time_group = models.TimeGroup.objects.filter(
			intervalsList__school_id = self.school.id
		).count()

		response = self.client.get(self.URL_TIMEGROUP_LIST)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


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

	def test_detail_timegroup_without_authentication(self):
		"""
			Generar [Error 401] "GET /officehour/time/:id" sin autenticación
		"""

		response = self.client.get(self.URL_TIMEGROUP_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



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
