import unittest, tempfile

from django.urls import reverse

from PIL import Image

from freezegun import freeze_time

from apps.school import models as school_models

from tests import faker

from tests.user.utils import create_user

from tests.school.utils import(
	create_news,
	create_school, 
	bulk_create_news, 
)

from .utils import testcases


def get_detail_news_url(id):
	return reverse(
		"management:news-detail",
		kwargs = {"pk": id}
	)


class NewsCreateAPITest(testcases.NewsCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_NEWS = self.get_school_news_url(school_id = self.school.id)

	def get_school_news_url(self, school_id):
		return reverse(
			"management:news-list-create", 
			kwargs={"pk": school_id}
		)

	def test_create_news(self):
		"""
			Validar "POST /news"
		"""

		self.client.force_authenticate(user = self.user_with_all_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			images = [ntf]
		
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


	def test_create_news_without_school_permission(self):
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


	def test_create_news_without_user_permission(self):
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


	def test_create_news_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /news" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		add_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

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


class NewsListAPITest(testcases.NewsListTestCase):
	def setUp(self):
		super().setUp()

		self.list_news = bulk_create_news(size = 5, school = self.school)

		self.URL_NEWS = self.get_school_news_url(school_id = self.school.id)

	def get_school_news_url(self, school_id, **extra):
		return reverse(
			"management:news-list-create", 
			kwargs={"pk": school_id},
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


	def test_get_news_without_school_permission(self):
		"""
			Generar [Error 403] "GET /news" de escuela que no tiene permiso de acceder
		"""
		other_school = create_school()

		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(
			self.get_school_news_url(school_id = other_school.id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_list_news_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /news" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_NEWS)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_news_filter_by_status(self):
		"""
			"GET /news" filtrados por estado de publicación ["publicado", "pendiente"]
		"""
		STATUS_PUBLISHED = "publicado"
		STATUS_PENDING = "pendiente"

		news_published = school_models.News.objects.filter(status = STATUS_PUBLISHED)
		news_pending = school_models.News.objects.filter(status = STATUS_PENDING)

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


class NewsDetailAPITest(testcases.NewsDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.news = create_news(school = self.school)

		self.URL_NEWS_DETAIL = get_detail_news_url(
			id = self.news.id
		)


	def test_detail_news(self):
		"""
			Validar "GET /news/:id"
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.get(self.URL_NEWS_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["title"], self.news.title)
		self.assertEqual(responseJson["school"], self.school.id)


	def test_detail_news_without_school_permission(self):
		"""
			Generar [Error 403] "GET /news/:id" por una noticia que pertenece a otra escuela
		"""
		
		self.client.force_authenticate(user = self.user_with_view_perm)

		other_school = create_school()
		news = create_news(school = other_school)

		response = self.client.get(
			get_detail_news_url(id = news.id)
		)

		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 403)


	def test_detail_news_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /news/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_NEWS_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_detail_news_without_authentication(self):
		"""
			Generar [Error 401] "GET /news/:id por usuarion sin autenticación"
		"""
		response = self.client.get(self.URL_NEWS_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class NewsUpdateAPITest(testcases.NewsDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.news = create_news(school = self.school)

		self.URL_NEWS_DETAIL = get_detail_news_url(
			id = self.news.id
		)

	def test_update_news(self):
		"""
			Validar "PUT/PATCH /news/:id"
		"""
		self.client.force_authenticate(user = self.user_with_update_perm)

		update_news = {
			"title": faker.text(max_nb_chars = 20),
			"description": faker.paragraph(),
		}

		response = self.client.patch(
			self.URL_NEWS_DETAIL,
			update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["title"], update_news["title"])
		self.assertEqual(responseJson["description"], update_news["description"])

		update_news = {
			"status": school_models.News.TypeStatus.pending
		}

		response = self.client.patch(
			self.URL_NEWS_DETAIL,
			update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["status"], update_news["status"])


	def test_update_news_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /news/:id" por intentar actualizar con datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_update_perm)

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
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_NEWS_DETAIL,
					case
				)

				responseStatus = response.status_code
				responseJson = response.data

				self.assertEqual(responseStatus, 400)


	def test_update_news_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /news/:id" por una noticia que pertenece a otra escuela
		"""

		self.client.force_authenticate(user = self.user_with_update_perm)

		other_school = create_school()
		news = create_news(school = other_school)

		update_news = {
			"title": faker.text(max_nb_chars = 20)
		}

		response = self.client.patch(
			get_detail_news_url(id = news.id),
			update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_news_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /news/:id" por falta de permiso de usuario
		"""

		test_cases = [
			{"user": self.user_with_view_perm},
			{"user": self.user_with_delete_perm},
		]

		update_news = {
			"title": faker.text(max_nb_chars = 20)
		}

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = case["user"])

				response = self.client.patch(
					self.URL_NEWS_DETAIL,
					update_news
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_update_news_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /news/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		update_news = {
			"title": faker.text(max_nb_chars = 20)
		}

		response = self.client.patch(
			self.URL_NEWS_DETAIL,
			update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_news_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /news/:id" por usuario sin autenticación
		"""
		update_news = {
			"title": faker.text(max_nb_chars = 20)
		}

		response = self.client.patch(
			self.URL_NEWS_DETAIL,
			update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class NewsDeleteAPITest(testcases.NewsDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.news = create_news(school = self.school)

		self.URL_NEWS_DETAIL = get_detail_news_url(
			id = self.news.id
		)

	def test_delete_news(self):
		"""
			Validar "DELETE /news/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_NEWS_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)


	def test_delete_news_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /news/:id" por una noticia que pertenece a otra escuela
		"""
		other_school = create_school()
		news = create_news(school = other_school)

		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(
			get_detail_news_url(id = news.id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_delete_news_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /news/:id" por falta de permiso de usuario
		"""
		test_cases = [
			{"user": self.user_with_view_perm},
			{"user": self.user_with_update_perm},
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = case["user"])
				
				response = self.client.delete(self.URL_NEWS_DETAIL)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_delete_news_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /news/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_NEWS_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_delete_news_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /news/:id" por usuario sin autenticación
		"""

		response = self.client.delete(self.URL_NEWS_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class NewsUpdateDeleteImagesAPITest(testcases.NewsDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.news = create_news(school = self.school)

		self.URL_NEWS_UPDATE_IMAGES = self.get_upload_image_url(
			id = self.news.id
		)
		self.URL_NEWS_DELETE_ALL_IMAGES = self.get_delete_all_image_url(
			id = self.news.id
		)

	def get_upload_image_url(self, id):
		return reverse(
			"management:news-upload-images",
			kwargs = {"pk": id}
		)

	def get_delete_all_image_url(self, id):
		return reverse(
			"management:news-delete-all-images",
			kwargs = {"pk": id}
		)

	@unittest.skip("Esta función aún no está completada")
	def test_update_news_images(self):
		"""
			Validar "PATCH /news-upload-images/:id"
		"""
		self.client.force_authenticate(user = self.user_with_update_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			images = [ntf]

			response = self.client.patch(
				self.URL_NEWS_UPDATE_IMAGES,
				{"media": images},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 200)


	def test_delete_all_news_images(self):
		"""
			Validar "DELETE /news-delete-all-images/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(
			self.URL_NEWS_DELETE_ALL_IMAGES
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertFalse(responseJson["media"])