import unittest, random, datetime

from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import (
	create_school,
	create_officehour,
	create_time_group,
	bulk_create_officehour,
	bulk_create_officehour_without_daysweek,
)
from tests.user.utils import create_user

from .utils import (
	set_time, 
	set_daysweek, 
	set_format_dasyweek_query,
	selected_daysweek_to_names
)
from .utils import testcases

from .utils.testcases_data import (
	UPDATE_OFFICEHOUR_WITH_WRONG_DATA
)

def get_school_officehour_url(school_id, **query):
	return reverse(
		"management:officehour-list-create",
		kwargs={"pk": school_id},
		**query
	)

def get_detail_officehour_url(id):
	return reverse(
		"management:officehour-detail",
		kwargs={"pk": id}
	)


class OfficeHourCreateAPITest(testcases.OfficeHourCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_OFFICEHOUR = get_school_officehour_url(
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

	def test_create_officehour_with_time_group_by_id(self):
		"""
			Validar "POST /officehour"
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)
		
		# Creamos un 'time_group' donde asociamos 
		# la escuela a la que pertecemos como admin

		time_group = create_time_group()
		
		create_officehour(
			school = self.school,
			time_group = time_group
		)
		
		self.create_officehour.pop("time_group")
		self.create_officehour.update({"time_group_id": time_group.id})

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 201)


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

	
	def test_create_officehour_with_time_group_id_does_not_exist(self):
		"""
			Generar [Error 400] "POST /officehour" por ID de time_group que no forma parte nuestra administración
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		time_group = create_time_group()
		
		create_officehour(
			time_group = time_group
		)

		self.create_officehour.pop("time_group")
		self.create_officehour.update({"time_group_id": time_group.id})

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 400)

	def test_create_officehour_with_invalid_time_group(self):
		"""
			Generar [Error 400] "POST /officehour" por enviar datos incorrectos para 'time_group'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		time_group = create_time_group()
		
		create_officehour(
			school = self.school,
			time_group = time_group
		)

		self.create_officehour.update({"time_group_id": time_group.id})

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 400)


	def test_create_officehour_without_time_group(self):
		"""
			Generar [Error 400] "POST /officehour" por no enviar datos para 'time_group'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.create_officehour.pop('time_group')

		response = self.client.post(
			self.URL_OFFICEHOUR,
			self.create_officehour
		)

		responseJson = response.data
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
			get_school_officehour_url(school_id = other_school.id),
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


class OfficeHourListAPITest(testcases.OfficeHourListTestCase):

	def setUp(self):
		super().setUp()

		self.officehours_list = bulk_create_officehour(size = 8, school = self.school)

		self.URL_OFFICEHOUR_LIST = get_school_officehour_url(
			school_id = self.school.id
		)

	def test_get_officehour(self):
		"""
			Validar "GET /officehour"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.URL_OFFICEHOUR_LIST
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(len(responseJson["results"]), len(self.officehours_list))

	def test_get_officehour_by_filter_active(self):
		"""
			Valiar "GET /officehour?is_active=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		yes_active = True
		no_active = False
		
		officehour_with_active_true = models.OfficeHour.objects.filter(
			time_group__active = yes_active
		)
		officehour_with_active_false = models.OfficeHour.objects.filter(
			time_group__active = no_active
		)

		response = self.client.get(
			get_school_officehour_url(
				school_id = self.school.id,
				query = {"is_active": yes_active}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["results"]), 
			officehour_with_active_true.count()
		)
		if responseJson["results"]:
			self.assertTrue(
				responseJson["results"][0]["time_group"]["active"]
			)


		response = self.client.get(
			get_school_officehour_url(
				school_id = self.school.id,
				query = {"is_active": no_active}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["count"], 
			officehour_with_active_false.count()
		)
		if responseJson["results"]:
			self.assertFalse(
				responseJson["results"][0]["time_group"]["active"]
			)


	def test_get_officehour_by_filter_dasyweek(self):
		"""
			Valiar "GET /officehour?days=[<...>,..]			
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		bulk_create_officehour(size = 10, school = self.school)

		# Indicamos por cuantos días a la semanas queremos hacer la busqueda
		# Ej: length = 2, [2,3]; length = 1, [4]
		selected_daysweek = set_daysweek(length = 1)

		officehour_selected_daysweek = models.OfficeHour.objects.filter(
			time_group__daysweek__day__in = selected_daysweek,
			school_id = self.school.id

		).distinct("id")

		response = self.client.get(
			get_school_officehour_url(
				school_id = self.school.id,
				query = {"days": set_format_dasyweek_query(
					selected = selected_daysweek
				)}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["count"],
			officehour_selected_daysweek.count()
		)



	def test_get_officehour_by_filter_dasyweek_null(self):
		"""
			Validar "GET /officehour?days_none=true"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_officehour_without_daysweek = 4
		isnull = True

		bulk_create_officehour_without_daysweek(
			school = self.school,
			size = total_officehour_without_daysweek
		)

		officehour_without_daysweek = models.OfficeHour.objects.filter(
			school_id = self.school.id,
			time_group__daysweek__isnull = isnull
		)

		response = self.client.get(
			get_school_officehour_url(
				school_id = self.school.id,
				query = {"undays": isnull}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["count"],
			officehour_without_daysweek.count()
		)

	def test_get_officehour_by_filter_description(self):
		"""
			Validar "GET /officehour?description__icontains=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		description = faker.text(max_nb_chars = 10)

		officehour = create_officehour(
			school = self.school,
			interval_description = description
		)

		search_description = description[:-3]
		# description[:-2] = omitimos los '3' útimos caracteres

		response = self.client.get(
			get_school_officehour_url(
				school_id = self.school.id,
				query = {"description": search_description}
				
			)
		)

		officehour_description = models.OfficeHour.objects.filter(
			school_id = self.school.id,
			interval_description__icontains = search_description
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertEqual(
			responseJson["count"],
			officehour_description.count()
		)


	def test_get_officehour_without_school_permission(self):
		"""
			Generar [Error 403] "GET /officehour" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_school_officehour_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_officehour_with_wrong_user(self):
		"""
			Validar "GET /officehour" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(
			self.URL_OFFICEHOUR_LIST
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_officehour_without_authentication(self):
		"""
			Validar "GET /officehour" sin autenticación
		"""
		response = self.client.get(
			self.URL_OFFICEHOUR_LIST
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class OfficeHourDetailAPITest(testcases.OfficeHourDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.officehour = create_officehour(school = self.school)

		self.URL_OFFICEHOUR_DETAIL = get_detail_officehour_url(
			id = self.officehour.id
		)

	def test_detail_officehour(self):
		"""
			Validar "GET /officehour/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.URL_OFFICEHOUR_DETAIL
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.officehour.id)
		self.assertEqual(
			responseJson["interval_description"],
			self.officehour.interval_description
		)
		self.assertEqual(responseJson["school"], self.officehour.school.id)

	def test_detail_officehour_without_school_permission(self):
		"""
			Generar [Error 403] "GET /officehour/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_officehour = create_officehour()

		response = self.client.get(
			get_detail_officehour_url(
				id = other_officehour.id
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_officehour_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /officehour/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(
			self.URL_OFFICEHOUR_DETAIL
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_officehour_without_authentication(self):
		"""
			Generar [Error 401] "GET /officehour/:id" por usuarion sin autenticación
		"""
		response = self.client.get(
			self.URL_OFFICEHOUR_DETAIL
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class OfficeHourUpdateAPITest(testcases.OfficeHourDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.officehour = create_officehour(school = self.school)

		self.URL_OFFICEHOUR_DETAIL = get_detail_officehour_url(
			id = self.officehour.id
		)

		self.update_officehour = {
			"description": faker.text(max_nb_chars = 30),
		}

	def test_update_officehour(self):
		"""
			Validar "PUT/PATCH /officehour/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.patch(
			self.URL_OFFICEHOUR_DETAIL,
			self.update_officehour
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.officehour.id)
		self.assertEqual(
			responseJson["interval_description"], 
			self.update_officehour["description"]
		)


	def test_update_officehour_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /officehour/:id" por enviar datos incorrectos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_cases = UPDATE_OFFICEHOUR_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_OFFICEHOUR_DETAIL,
					case
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_update_officehour_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /officehour/:id" por actualizar información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		other_officehour = create_officehour(
			school = create_school()
		)

		response = self.client.patch(
			get_detail_officehour_url(
				id = other_officehour.id
			),
			self.update_officehour
		)

		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 403)


	def test_update_officehour_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /officehour/:id" por falta de permiso de usuario
		"""
		test_cases = [
			{"user": self.user_with_view_perm},
			{"user": self.user_with_delete_perm},
			{"user": self.user_with_add_perm},
		]

		for case in test_cases:
			with self.subTest(case = case):
				
				self.client.force_authenticate(user = case["user"])
				
				response = self.client.patch(
					self.URL_OFFICEHOUR_DETAIL,
					self.update_officehour
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_update_officehour_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /officehour/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_OFFICEHOUR_DETAIL,
			self.update_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_officehour_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /officehour/:id" por usuario sin autenticación
		"""

		response = self.client.patch(
			self.URL_OFFICEHOUR_DETAIL,
			self.update_officehour
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class OfficeHourDeleteAPITest(testcases.OfficeHourDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.officehour = create_officehour(school = self.school)

		self.URL_OFFICEHOUR_DETAIL = get_detail_officehour_url(
			id = self.officehour.id
		)


	def test_delete_officehour(self):
		"""
			Validar "DELETE /officehour/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_OFFICEHOUR_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_officehour_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /officehour/:id" por eliminar información que pertenece a otra escuela
		"""
		self.client.force_authenticate( user = self.user_with_delete_perm)

		officehour = create_officehour(
			school = create_school()
		)

		response = self.client.delete(
			get_detail_officehour_url(id = officehour.id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_officehour_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /officehour/:id" por falta de permiso de usuario
		"""
		test_cases = [
			{"user": self.user_with_add_perm},
			{"user": self.user_with_change_perm},
			{"user": self.user_with_view_perm},
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = case["user"])

				response = self.client.delete(
					self.URL_OFFICEHOUR_DETAIL
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_delete_officehour_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /officehour/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_OFFICEHOUR_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_delete_officehour_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /officehour/:id" por usuario sin autenticación
		"""

		response = self.client.delete(self.URL_OFFICEHOUR_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)