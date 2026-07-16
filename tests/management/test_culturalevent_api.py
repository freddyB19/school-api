import tempfile, datetime
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta 

from apps.school import models

from PIL import Image
from freezegun import freeze_time

from apps.school import models

from tests import faker

from tests.school.utils import (
	create_school,
	create_cultural_event,
	bulk_create_cultural_event
)

from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data, list_upload_files

def get_create_list_culturalevent_url(school_id, **extra):
	return reverse(
		"management:culturalevent-list-create",
		kwargs={"pk": school_id},
		**extra
	)

def get_detail_culturalevent_url(pk):
	return reverse(
		"management:culturalevent-detail",
		kwargs={"pk": pk},
	)


class CulturalEventCreateAPITest(testcases.CulturalEventCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_CULTURALEVENT_CREATE = get_create_list_culturalevent_url(
			school_id = self.school.id
		)

		self.add_cultural_event = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CULTURALEVENT_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year(),
		}

	def test_create_culturalevent(self):
		"""
			Validar "POST /culturalevent" 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_cultural_event.update({"media": [ntf]})

			response = self.client.post(
				self.URL_CULTURALEVENT_CREATE,
				self.add_cultural_event,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertEqual(responseJson["title"], self.add_cultural_event["title"])
			self.assertEqual(responseJson["description"], self.add_cultural_event["description"])
			
			if self.add_cultural_event["media"]:
				total_media = len(self.add_cultural_event["media"])

				self.assertTrue(responseJson["media"])
				self.assertEqual(len(responseJson["media"]), total_media)

	def test_create_culturalevent_without_description(self):
		"""
			Validar "POST /culturalevent" sin descripción
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_cultural_event.update({"media": [ntf]})
			self.add_cultural_event.pop("description")

			response = self.client.post(
				self.URL_CULTURALEVENT_CREATE,
				self.add_cultural_event,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertEqual(responseJson["title"], self.add_cultural_event["title"])
			self.assertIsNone(responseJson["description"])
			
			if self.add_cultural_event["media"]:
				total_media = len(self.add_cultural_event["media"])

				self.assertTrue(responseJson["media"])
				self.assertEqual(len(responseJson["media"]), total_media)

	
	def test_create_culturalevent_without_media(self):
		"""
			Validar "POST /culturalevent" sin 'media' (imágenes)
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_CULTURALEVENT_CREATE,
			self.add_cultural_event,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson["title"], self.add_cultural_event["title"])
		self.assertEqual(responseJson["description"], self.add_cultural_event["description"])
		self.assertFalse(responseJson["media"])


	def test_create_culturalevent_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /culturalevent" por  enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_case = testcases_data.CREATE_CULTURAL_EVENT_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
					img = Image.new("RGB", (10, 10))
					img.save(ntf, format="JPEG")
					ntf.seek(0)

					case.update({"media": [img]})

					response = self.client.post(
						self.URL_CULTURALEVENT_CREATE,
						case,
						format="multipart"
					)

					responseJson = response.data
					responseStatus = response.status_code

					self.assertEqual(responseStatus, 400)

	def test_create_culturalevent_without_school_permission(self):
		"""
			Generar [Error 403] "POST /culturalevent" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			get_create_list_culturalevent_url(
				school_id = other_school.id
			),
			self.add_cultural_event,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_culturalevent_without_user_permission(self):
		"""
			Generar [Error 403] "POST /culturalevent" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_CULTURALEVENT_CREATE,
			self.add_cultural_event,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_culturalevent_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /culturalevent" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()

		user.user_permissions.set(
			get_permissions(codenames = [
				"add_culturalevent"
			])
		)
		
		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_CULTURALEVENT_CREATE,
			self.add_cultural_event,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_create_culturalevent_without_authentication(self):
		"""
			Generar [Error 401] "POST /culturalevent" sin autenticar  
		"""
		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_cultural_event.update({"media": [ntf]})

			response = self.client.post(
				self.URL_CULTURALEVENT_CREATE,
				self.add_cultural_event,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 401)


class CulturalEventListAPITest(testcases.CulturalEventTestCase):
	def setUp(self):
		super().setUp()

		self.URL_CULTURALEVENT_LIST = get_create_list_culturalevent_url(
			school_id = self.school.id
		)

		bulk_create_cultural_event(
			size = 6,
			school = self.school,
			date = self.create_date()
		)

		bulk_create_cultural_event(school = self.school, size = 10)

	def create_date(self, input_month: int = None) -> datetime.date:
		local_time = timezone.localtime()
		month = local_time.month if not input_month else input_month
		year = local_time.year
		
		current_date = datetime.date(
			year, month, faker.random_int(min = 1, max = 25)
		)

		return current_date


	def test_get_cultural_event(self):
		"""
			Validar "GET /culturalevent"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_culturalevent = models.CulturalEvent.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_CULTURALEVENT_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_culturalevent)
	
	def test_get_cultural_event_filter_by_title(self):
		"""
			Validar "GET /culturalevent?title=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		title = faker.word()
		for _ in range(2):
			create_cultural_event(school = self.school, title = f"{title} {faker.word()}")

		total_culturalevent = models.CulturalEvent.objects.filter(
			school_id = self.school.id,
			title__icontains = title
		).count()

		response = self.client.get(get_create_list_culturalevent_url(
			school_id = self.school.id,
			query = {"title": title}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_culturalevent)

	def test_get_cultural_event_filter_by_month(self):
		"""
			Validar "GET /culturalevent?month=<...>&year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		month = faker.random_int(min = 1, max = 12)

		date = self.create_date(input_month = month)
		other_date = datetime.date(2024, month, faker.random_int(min = 1, max = 25))

		bulk_create_cultural_event(
			size = 3,
			date = date,
			school = self.school
		)

		bulk_create_cultural_event(
			size = 2,
			date = other_date,
			school = self.school
		)

		total_culturalevent = models.CulturalEvent.objects.filter(
			school_id = self.school.id,
			date__month = date.month,
			date__year = date.year
		).count()


		response = self.client.get(
			get_create_list_culturalevent_url(
				school_id = self.school.id,
				query = {"month": date.month, "year": date.year}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_culturalevent)

	def test_get_cultural_event_filter_by_year(self):
		"""
			Validar "GET /culturalevent?year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		date_1 = faker.date_between(start_date = "-4y", end_date = "-1y")
		date_2 = faker.date_between(start_date = "now", end_date = "+4y")

		with freeze_time(f"{date_1.year}-01-01") as frozen_time:
			for _ in range(1, 13):
				bulk_create_cultural_event(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				current_date = datetime.datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		with freeze_time(f"{date_2.year}-01-01") as frozen_time:
			for _ in range(1, 13):
				bulk_create_cultural_event(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				current_date = datetime.datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		date_1_year = date_1.year
		date_2_year = date_2.year

		test_case = [

			{
				"filter": {"year": date_1_year},
				"total_count": models.CulturalEvent.objects.filter(
					school_id = self.school.id,
					date__year = date_1_year
				).count()
			},
			{
				"filter": {"year": date_2_year},
				"total_count": models.CulturalEvent.objects.filter(
					school_id = self.school.id,
					date__year = date_2_year
				).count()
			}
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(
					get_create_list_culturalevent_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 200)
				self.assertEqual(responseJson["count"], case["total_count"])
	
	def test_get_cultural_event_filter_by_date_range(self):
		"""
			Validar "GET /culturalevent?date_after=<...>&date_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		event_date = f"{current_year}-01-01"
		with freeze_time(event_date) as frozen_time:
			for _ in range(1, 13):
				bulk_create_cultural_event(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				current_date = datetime.datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		format_month_str = lambda month: f'0{month}' if month < 10 else month
		month_start = format_month_str(month = faker.random_int(min = 1, max = 5))
		month_end = format_month_str(month = faker.random_int(min = 6, max = 12))

		event_date_start_str = f"{current_year}-{month_start}-01"
		event_date_end_str = f"{current_year}-{month_end}-30"

		event_date_start = datetime.datetime.fromisoformat(event_date_start_str).date()
		event_date_end = datetime.datetime.fromisoformat(event_date_end_str).date()

		total_culturalevent = models.CulturalEvent.objects.filter(
			school_id = self.school.id,
			date__range = (event_date_start, event_date_end)
		).count()

		response = self.client.get(
			get_create_list_culturalevent_url(
				school_id = self.school.id,
				query = {
					"date_after": event_date_start_str, 
					"date_before": event_date_end_str
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_culturalevent)

	def test_get_cultural_event_filter_by_date_after_or_date_before(self):
		"""
			Validar "GET /culturalevent?date_after=<...> | date_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		event_date = f"{current_year}-01-01"
		with freeze_time(event_date) as frozen_time:
			for _ in range(1, 13):
				bulk_create_cultural_event(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				current_date = datetime.datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		format_month_str = lambda month: f'0{month}' if month < 10 else month
		month_before = format_month_str(month = faker.random_int(min = 1, max = 5))
		month_after = format_month_str(month = faker.random_int(min = 6, max = 12))

		event_date_before_str = f"{current_year}-{month_before}-01"
		event_date_after_str = f"{current_year}-{month_after}-30"

		event_date_before = datetime.datetime.fromisoformat(event_date_before_str).date()
		event_date_after = datetime.datetime.fromisoformat(event_date_after_str).date()

		test_case = [
			{
				"filter": {"date_before": event_date_before_str},
				"total_count": models.CulturalEvent.objects.filter(
					school_id = self.school.id,
					date__lte = event_date_before
				).count()
			},
			{
				"filter": {"date_after": event_date_after_str},
				"total_count": models.CulturalEvent.objects.filter(
					school_id = self.school.id,
					date__gte = event_date_after
				).count()
			}
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(get_create_list_culturalevent_url(
					school_id = self.school.id,
					query = case["filter"]
				))

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 200)
				self.assertEqual(responseJson["count"], case["total_count"])

	def test_get_cultural_event_without_school_permission(self):
		"""
			Validar "GET /culturalevent?month=<...>&year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		other_school = create_school()
		
		bulk_create_cultural_event(school = other_school ,size = 5)

		response = self.client.get(
			get_create_list_culturalevent_url(
				school_id = other_school.id
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_cultural_event_without_wrong_user(self):
		"""
			Validar "GET /culturalevent?month=<...>&year=<...>"
		"""
		user = create_user()

		user.user_permissions.set(
			get_permissions(codenames = ["view_culturalevent"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_CULTURALEVENT_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_cultural_event_without_authenticate(self):
		"""
			Validar "GET /culturalevent?month=<...>&year=<...>"
		"""
		response = self.client.get(self.URL_CULTURALEVENT_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CulturalEventDetailAPITest(testcases.CulturalEventDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.cultural_event = create_cultural_event(
			school = self.school
		)

		self.URL_CULTURALEVENT_DETAIL = get_detail_culturalevent_url(
			pk = self.cultural_event.id
		)

	def test_detail_cultural_event(self):
		"""
			Validar "GET /culturalevent/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_CULTURALEVENT_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultural_event.id)
		self.assertEqual(responseJson["title"], self.cultural_event.title)
		self.assertEqual(responseJson["description"], self.cultural_event.description)
		self.assertEqual(len(responseJson["media"]), self.cultural_event.media.count())

	def test_detail_cultural_event_without_school_permission(self):
		"""
			Generar [Error 403] "GET /culturalevent/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		cultural_event = create_cultural_event() 

		response = self.client.get(
			get_detail_culturalevent_url(pk = cultural_event.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_cultural_event_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /culturalevent/:id" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["view_culturalevent"])
		)

		self.client.force_authenticate(user = user)

		cultural_event = create_cultural_event() 

		response = self.client.get(self.URL_CULTURALEVENT_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_cultural_event_without_authentication(self):
		"""
			Generar [Error 401] "GET /culturalevent/:id" sin autenticar
		"""
		response = self.client.get(self.URL_CULTURALEVENT_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CulturalEventDeleteAPITest(testcases.CulturalEventDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.cultural_event = create_cultural_event(school = self.school)

		self.URL_CULTURALEVENT_DELETE = get_detail_culturalevent_url(
			pk = self.cultural_event.id
		)

	def test_delete_cultural_event(self):
		"""
			Validar "DELETE /culturalevent/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_CULTURALEVENT_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_cultural_event_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /culturalevent/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		cultural_event = create_cultural_event()

		response = self.client.delete(
			get_detail_culturalevent_url(pk = cultural_event.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_cultural_event_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /culturalevent/:id" por falta de permiso de usuario
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_CULTURALEVENT_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_cultural_event_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /culturalevent/:id" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_culturalevent"])
		)
		
		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_CULTURALEVENT_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_cultural_event_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /culturalevent/:id" sin autenticar
		"""
		response = self.client.delete(self.URL_CULTURALEVENT_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CulturalEventUpdateAPITest(testcases.CulturalEventDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.cultural_event = create_cultural_event(school = self.school)

		self.URL_CULTURALEVENT_UPDATE = get_detail_culturalevent_url(
			pk = self.cultural_event.id
		)

		self.update_cultural_event = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CULTURALEVENT_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year(),
		}

		self.partial_cultural_event = {
			"description": faker.paragraph(),
		}

	def test_update_cultural_event(self):
		"""
			Validar "PUT/PATCH /culturalevent/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.put(
			self.URL_CULTURALEVENT_UPDATE,
			self.update_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultural_event.id)
		self.assertEqual(responseJson["title"], self.update_cultural_event["title"])
		self.assertEqual(responseJson["description"], self.update_cultural_event["description"])

		self.assertNotEqual(responseJson["title"], self.cultural_event.title)
		self.assertNotEqual(responseJson["description"], self.cultural_event.description)
		self.assertNotEqual(responseJson["date"], self.cultural_event.date)

		ce = models.CulturalEvent.objects.get(pk = self.cultural_event.id)

		# PATCH /culturalevent/:id

		response = self.client.patch(
			self.URL_CULTURALEVENT_UPDATE,
			self.partial_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultural_event.id)
		self.assertEqual(responseJson["description"], self.partial_cultural_event["description"])


	def test_update_culturalevent_with_data_already_exists(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" por datos duplicados
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		cultural_event = create_cultural_event(
			school = self.school,
			title = self.cultural_event.title
		)

		response = self.client.patch(
			self.URL_CULTURALEVENT_UPDATE,
			{"date": cultural_event.date}
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

		cultural_event = create_cultural_event(
			school = self.school,
			date = self.cultural_event.date
		)

		response = self.client.patch(
			self.URL_CULTURALEVENT_UPDATE,
			{"title": cultural_event.title}
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_update_cultural_event_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" por datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)
	
		test_case = testcases_data.UPDATE_CULTURAL_EVENT_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_CULTURALEVENT_UPDATE,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)

	def test_update_cultural_event_without_school_permission(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		cultural_event = create_cultural_event()
		
		response = self.client.patch(
			get_detail_culturalevent_url(pk = cultural_event.id),
			self.partial_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_cultural_event_without_user_permission(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.patch(
			self.URL_CULTURALEVENT_UPDATE,
			self.partial_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_cultural_event_with_wrong_user(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_culturalevent"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.put(
			self.URL_CULTURALEVENT_UPDATE,
			self.update_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_cultural_event_without_authentication(self):
		"""
			Generar [Error 400] "PUT/PATCH /culturalevent/:id" sin autenticar
		"""
		response = self.client.put(
			self.URL_CULTURALEVENT_UPDATE,
			self.update_cultural_event
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
