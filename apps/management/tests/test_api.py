import unittest, tempfile

from django.urls import reverse
from django.test import TransactionTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from freezegun import freeze_time

from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from apps.user.tests.utils.utils import (
	create_user, 
	create_permissions, 
	get_permissions
)
from apps.school.tests.utils.utils import(
	create_news,
	create_school, 
	bulk_create_news, 
)
from apps.school import models as school_models
from apps.management import models
from apps.management.apiv1 import views

from . import faker
from .utils.utils import (
	get_administrator, 
	create_list_images
)
from .utils.testcases import (
	UPDATE_SCHOOL_WITH_WRONG_DATA, 
	NewsTest,
	NewsListTest,
	NewsCreateTest,
	SchoolUpdateTest
)



class AdministratorAPITest(TransactionTestCase):

	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1, email = "carlos@example.com")
		self.administrator = get_administrator(school_id = self.school.id)
		self.administrator.users.set([self.user_role_admin, self.user_role_staff])


		self.URL_ADMINISTRATOR = reverse(
			"management:administrator", 
			kwargs={"school_id": self.school.id}
		) 
		self.URL_ADMINISTRATOR_DETAIL = reverse(
			"management:administrator-detail", 
			kwargs={"pk": self.administrator.id}
		)
		

	def test_get_administrator(self):
		"""
			Validar endpoint administrator
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertLessEqual(len(responseJson["users"]), 5)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())


	def test_get_administrator_does_not_existent_school(self):
		"""
			Intentar acceder a la información de 'administrator' con un ID de escuela que no existe
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		wrong_school_id = 100
		
		response = self.client.get(reverse(
			"management:administrator", 
			kwargs={"school_id": wrong_school_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores del portal de un colegio con ID: {wrong_school_id}")

	def test_get_administrator_without_authentication(self):
		"""
			Accediendo a la información de 'administrator' sin autenticación del usuario
		"""
		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


	def test_get_detail_administrator(self):
		"""
			Validar endpoint administrator-detail
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		response = self.client.get(self.URL_ADMINISTRATOR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())
		self.assertEqual(responseJson["school"]["id"], self.school.id)
		self.assertEqual(responseJson["school"]["name"], self.school.name)


	def test_get_detail_administrator_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint administrator-detail
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		wrong_id = 120
		
		response = self.client.get(reverse(
			"management:administrator-detail", 
			kwargs={"pk": wrong_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores de este portal con ID: {wrong_id}")
	

	def test_get_detail_administrator_without_authentication(self):
		"""
			Accediendo al endpoint 'administrator-detail' sin autenticación
		"""
		response = self.client.get(self.URL_ADMINISTRATOR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class UserUpdatePermissionsTest(TransactionTestCase):
	
	def setUp(self):
		create_permissions()

		self.client = APIClient()

		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1, email = "carlos@example.com")

		create_permissions("Create test", "create_test")
		create_permissions("Read test", "read_test")
		create_permissions("Delete test", "delete_test")
		create_permissions("Update test", "update_test")

		self.URL_USER_PERMISSIONS = reverse(
			"management:user-permission",
			kwargs={"pk": self.user_role_staff.id}
		)


	def test_update_permission_user(self):
		"""
			Actualizar los permisos de un usuario
		"""
		self.client.force_authenticate(user = self.user_role_admin)

		update_user_permissions = {
			"permissions": ["create_test", "update_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["user_permissions"]),
			len(update_user_permissions["permissions"])
		)


		# Definiendo solo un permiso

		update_user_permissions = {
			"permissions": ["delete_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["user_permissions"], 
			update_user_permissions["permissions"]
		)


	def test_update_permission_user_without_permission_role(self):
		"""
			Intentando actualizar los permisos de un usuario tendiendo como user.role = 'staff'
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		user = create_user(role = 1, email = "user1@example.com")

		update_user_permissions = {
			"permissions": ["create_test", "delete_test"]
		}

		response = self.client.patch(
			reverse(
				"management:user-permission",
				kwargs={"pk": user.id}
			),
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_permission_user_without_authentication(self):
		"""
			Intentando actualizar los permisos de un usuario sin autenticación
		"""
		user = create_user(role = 1, email = "user1@example.com")

		update_user_permissions = {
			"permissions": ["create_test", "delete_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class SchoolUpdateAPITest(SchoolUpdateTest):
	def setUp(self):
		super().setUp()

		self.URL_SCHOOL_UPDATE = self.get_detail_url(id = self.school.id)

	def get_detail_url(self, id):
		return reverse(
			"management:school-detail",
			kwargs={"pk": id}
		)


	def test_update_school(self):
		"""
			Actualizando la información de una escuela
		"""
		self.client.force_authenticate(user = self.user_with_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}

		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertNotEqual(responseJson["name"], self.school.name)
		self.assertNotEqual(responseJson["history"], self.school.history)


	def test_update_school_does_not_exist(self):
		"""
			Actualizando la información de una escuela que no existe
		"""

		self.client.force_authenticate(user = self.user_with_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}

		wrong_id = 12

		response = self.client.patch(
			self.get_detail_url(id = wrong_id),
			update_school
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_update_school_without_user_permission(self):
		"""
			Actualizando la información de una escuela sin permiso de usuario
		"""

		self.client.force_authenticate(user = self.user_without_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}
		
		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_school_with_wrong_data(self):
		"""
			Enviando datos erroneos para actualizar una escuela
		"""
		test_cases = UPDATE_SCHOOL_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = self.user_with_perm)
				response = self.client.patch(
					self.URL_SCHOOL_UPDATE,
					case["update"]
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, case["expect"]["code"])
				self.assertTrue(case["expect"]["field"] in responseJson)


	def test_update_school_without_authentication(self):
		"""
			Actualizando la información de una escuela sin autenticación del usuario
		"""

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}
		
		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class SchoolUpdateLogoAPITest(SchoolUpdateTest):
	def setUp(self):
		super().setUp()

		self.URL_SCHOOL_UPDATE_LOGO = self.get_upload_image_url(id = self.school.id)

	def get_upload_image_url(self, id):
		return reverse(
			"management:school-upload-image",
			kwargs = {"pk": id}
		)


	@unittest.skip("Esta función aun no está completada")
	def test_update_school_logo(self):
		"""
			Actualizando el logo de una escuela
		"""

		self.client.force_authenticate(user = self.user_with_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as temp_file:
			image = Image.new("RGB", (10, 10))
			image.save(temp_file, format="JPEG")
			temp_file.seek(0)

			response = self.client.patch(
				self.URL_SCHOOL_UPDATE_LOGO,
				{"logo": temp_file},
				format="multipart"
			)


		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertNotEqual(responseJson["logo"], self.school.logo)



class NewsCreateAPITest(NewsCreateTest):
	def setUp(self):
		super().setUp()

		self.URL_NEWS = self.get_school_news_url(school_id = self.school.id)

	def get_school_news_url(self, school_id):
		return reverse(
			"management:news-list-create", 
			kwargs={"school_id": school_id}
		)

	def test_create_news(self):
		"""
			Validar "POST /news"
		"""

		self.client.force_authenticate(user = self.user_with_all_perm)

		images = create_list_images()
		
		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph(),
			"media": images
		}

		response = self.client.post(
			self.URL_NEWS,
			add_news,
			format="multipart"
		)

		for image in images:
			image.close()

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson["title"], add_news["title"])
		self.assertEqual(responseJson["description"], add_news["description"])
		self.assertEqual(responseJson["status"], "publicado")


	def test_create_news_without_images(self):
		"""
			Validar "POST /news" sin enviar imagenes
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		response = self.client.post(
			self.URL_NEWS,
			add_news,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson["title"], add_news["title"])
		self.assertEqual(responseJson["description"], add_news["description"])
		self.assertEqual(responseJson["status"], "publicado")
		self.assertEqual(len(responseJson["media"]), 0)


	def test_create_news_with_wrong_data(self):
		"""
			Generar [Error 400] en "POST /news" por enviar datos invalidos
		"""
		
		self.client.force_authenticate(user = self.user_with_all_perm)

		test_cases = [
			{
				"title": "Text"
			},
			{
				"title": faker.text(max_nb_chars=200)
			},
			{
				"title": faker.text(max_nb_chars=20),
				"status": "pausado"
			},
		]

		for case in test_cases:
			with self.subTest(case  = case):
				response = self.client.post(
					self.URL_NEWS,
					case,
				)
				
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)


	def test_create_news_without_permission_school(self):
		"""
			Generar [Error 403] "GET /news" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		other_school = create_school()

		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		response = self.client.post(
			self.get_school_news_url(school_id = other_school.id),
			add_news,
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_create_news_with_permission(self):
		"""
			Generar [Error 403] en "POST /news" por usuarios sin permisos para crear una noticia
		"""

		test_cases = [
			{"user": self.user_with_view_perm},
			{"user": self.user_with_delete_perm},
		]

		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		for case in test_cases:
			with self.subTest(case  = case):
				self.client.force_authenticate(user = case["user"])

				response = self.client.post(
					self.URL_NEWS,
					add_news,
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_create_news_without_authentication(self):
		"""
			Generar [Error 401] en "POST /news" no autenticarse
		"""

		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		response = self.client.post(
			self.URL_NEWS,
			add_news,
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class NewsListAPITest(NewsListTest):
	def setUp(self):
		super().setUp()

		self.list_news = bulk_create_news(size = 5, school = self.school)

		self.URL_NEWS = self.get_school_news_url(school_id = self.school.id)

	def get_school_news_url(self, school_id, **extra):
		return reverse(
			"management:news-list-create", 
			kwargs={"school_id": school_id},
			**extra
		)

	def delete_all_news(self):
		school_models.News.objects.all().delete()

	
	def test_get_news(self):
		"""
			Validar "GET /news" 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_NEWS)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(len(responseJson["results"]), len(self.list_news))


	def test_get_news_without_permission_school(self):
		"""
			Generar [Error 403] "GET /news" de escuela que no tiene permiso de acceder
		"""
		other_school = create_school()

		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.get_school_news_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_news_filter_by_status(self):
		"""
			"GET /news" filtrados por estado de publicación ["publicado", "pendiente"]
		"""
		STATUS_PUBLISHED = "publicado"
		STATUS_PENDING = "pendiente"

		news_published = list(
			filter(lambda news: news.status == STATUS_PUBLISHED, self.list_news)
		)
		news_pending = list(
			filter(lambda news: news.status == STATUS_PENDING, self.list_news)
		)

		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"status": STATUS_PUBLISHED}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(len(responseJson["results"]), len(news_published))

		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"status": STATUS_PENDING}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(len(responseJson["results"]), len(news_pending))


	def test_get_news_filter_by_date(self):
		"""
			"GET /news" filtrados por creación/actualización [año, mes, día]
		"""
		self.delete_all_news()

		self.client.force_authenticate(user = self.user_with_all_perm)

		SEARCH_NEWS_UPDATE_DAY = 20
		SEARCH_NEWS_CREATE_MONTH_OCT = 10
		SEARCH_NEWS_CREATE_MONTH_NOV = 11
		SEARCH_NEWS_CREATE_YEAR = 2023

		with freeze_time(f"2025-{SEARCH_NEWS_CREATE_MONTH_OCT}-10"):
			news_create_oct = bulk_create_news(size = 3, school= self.school)

		with freeze_time(f"2025-{SEARCH_NEWS_CREATE_MONTH_NOV}-10"):
			news_create_nov = bulk_create_news(size = 5, school = self.school)
		
		with freeze_time(f"{SEARCH_NEWS_CREATE_YEAR}-04-10"):
			news_create_year = bulk_create_news(size = 2, school = self.school)

		with freeze_time(f"2026-10-{SEARCH_NEWS_UPDATE_DAY} 12:30:30"):
			news_update_day = news_create_oct.copy()[0]
			news_update_day.title = faker.text(max_nb_chars = 20)
			news_update_day.save()
		
			news_update_day.refresh_from_db()

			total_news_updated = 1


		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"created_month": SEARCH_NEWS_CREATE_MONTH_OCT}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["results"]), 
			len(news_create_oct)
		)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"created_month": SEARCH_NEWS_CREATE_MONTH_NOV}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["results"]), 
			len(news_create_nov)
		)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"updated_day": SEARCH_NEWS_UPDATE_DAY}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertGreaterEqual(
			len(responseJson["results"]), 
			total_news_updated
		)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"created_year": SEARCH_NEWS_CREATE_YEAR}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["results"]), 
			len(news_create_year)
		)



	def test_get_news_without_authentication(self):
		"""
			"GET /news" sin autenticación de usuario
		"""

		response = self.client.get(self.URL_NEWS)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
