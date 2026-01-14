import unittest, tempfile, datetime

from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta 

from PIL import Image
from freezegun import freeze_time

from apps.school import models

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

set_format_number = lambda number: f"0{number}" if number < 10 else number

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
		models.News.objects.all().delete()

	
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
			Validar "GET /news?status=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		STATUS_PUBLISHED = models.News.TypeStatus.published
		STATUS_PENDING =  models.News.TypeStatus.pending

		news_published = models.News.objects.filter(
			school_id = self.school.id,
			status = STATUS_PUBLISHED
		)
		news_pending = models.News.objects.filter(
			school_id = self.school.id,
			status = STATUS_PENDING
		)

		test_case = [
			{
				"filter": {"status": STATUS_PUBLISHED},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					status = STATUS_PUBLISHED
				).count()
			},
			{
				"filter": {"status": STATUS_PENDING},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					status = STATUS_PENDING
				).count()
			},

		]

		for case in test_case:
			response = self.client.get(
				self.get_school_news_url(
					school_id = self.school.id,
					query = case["filter"]
				)
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 200)
			self.assertEqual(responseJson["count"], case["total"])

	def test_get_news_filter_by_created_day(self):
		"""
			Validar "GET /news?created_day=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_date = timezone.localtime()

		create_date = f"{current_date.year}-{current_date.month}-01 {faker.time()}"
		with freeze_time(create_date) as frozen_time:
			for _ in range(26):
				bulk_create_news(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				frozen_time.tick(delta = datetime.timedelta(days = 1))

		search_day = faker.random_int(min = 1, max = 25)
		format_day = set_format_number(search_day)

		past_date = faker.date_between(start_date = "-5y", end_date = "-2y")

		create_date = f"{past_date.year}-{past_date.month}-{format_day} {faker.time()}"
		with freeze_time(create_date):
			bulk_create_news(
				size = faker.random_int(min = 1, max = 10),
				school = self.school
			)

		total_news_by_fulldate = models.News.objects.filter(
			school_id = self.school.id,
			created__day = search_day,
			created__month = current_date.month,
			created__year = current_date.year
		).count()

		total_news_by_day = models.News.objects.filter(
			school_id = self.school.id,
			created__day = search_day
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"created_year": current_date.year,
					"created_month": current_date.month,
					"created_day": search_day
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_fulldate)

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"created_day": search_day
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_day)

	def test_get_news_filter_by_created_month(self):
		"""
			Validar "GET /news?created_month=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		create_date = f"{current_year}-01-01 {faker.time()}"
		with freeze_time(create_date) as frozen_time:
			for _ in range(1, 13):
				bulk_create_news(
					size = faker.random_int(min = 1, max = 10),
					school = self.school
				)

				current_date = datetime.datetime.now()
				target_time = current_date + relativedelta(months=1)
				delta = target_time - current_date
				frozen_time.tick(delta = delta)

		search_month = faker.random_int(min = 1, max = 12)
		format_month = set_format_number(search_month)

		past_date = faker.date_between(start_date = "-5y", end_date = "-2y")

		create_date = f"{past_date.year}-{format_month}-01 {faker.time()}"
		with freeze_time(create_date):
			bulk_create_news(
				size = faker.random_int(min = 1, max = 10),
				school = self.school
			)

		total_news_by_year_month = models.News.objects.filter(
			school_id = self.school.id,
			created__year = current_year,
			created__month = search_month
		).count()

		total_news_by_month = models.News.objects.filter(
			school_id = self.school.id,
			created__month = search_month
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"created_year": current_year,
					"created_month": search_month
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_year_month)
		
		#

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"created_month": search_month
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_month)

	def test_get_news_filter_by_created_year(self):
		"""
			Validar "GET /news?created_year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		start_date = faker.date_between(start_date = "-5y", end_date = "-1y")

		list_years = []

		with freeze_time(start_date) as frozen_time:
			for _ in range(3):
				bulk_create_news(
					size = faker.random_int(min = 10, max = 50),
					school = self.school
				)

				current_date = datetime.datetime.now()
				target_time = current_date + relativedelta(years=1)
				delta = target_time - current_date
				frozen_time.tick(delta = delta)

				list_years.append(current_date.year)

		search_year = faker.random_element(elements = list_years)

		total_news_by_year = models.News.objects.filter(
			school_id = self.school.id,
			created__year = search_year
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"created_year": search_year,
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_year)

	def test_get_news_filter_by_created(self):
		"""
			Validar "GET /news?created_*=<...>"
			- Por rango de fecha.
			- Después de una fecha.
			- Antes de una fecha.
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		current_date = f"{current_year}-01-01 {faker.time()}"
		with freeze_time(current_date) as frozen_time:
			for _ in range(13):
				bulk_create_news(
					size = faker.random_int(min = 1, max = 15),
					school = self.school
				)

				current_date = datetime.datetime.now()
				target_time = current_date + relativedelta(months=1)
				delta = target_time - current_date
				frozen_time.tick(delta = delta)

		format_datetime = "%Y-%m-%d %H:%M:%S"
		format_month_after = set_format_number(faker.random_int(min = 1, max = 5))
		format_month_before = set_format_number(faker.random_int(min = 6, max = 12))

		created_after_string = f"{current_year}-{format_month_after}-01 00:00:00"
		created_before_string = f"{current_year}-{format_month_before}-30 23:59:59"

		created_after = timezone.make_aware(
			datetime.datetime.strptime(created_after_string, format_datetime)
		)
		created_before = timezone.make_aware(
			datetime.datetime.strptime(created_before_string, format_datetime)
		)

		test_case = [
			{
				"filter": {
					"created_after": created_after_string,
					"created_before": created_before_string
				},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					created__range = (created_after, created_before)
				).count()
			},
			{
				"filter": {"created_after": created_after_string},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					created__gte = created_after
				).count()
			},
			{
				"filter": {"created_before": created_before_string},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					created__lte = created_before
				).count()
			}
		]

		for case in test_case:
			with self.subTest(case = case):

				response = self.client.get(
					self.get_school_news_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 200)
				self.assertEqual(responseJson["count"], case["total"])

	def test_get_news_filter_by_update_day(self):
		"""
			Validar "GET /news?updated_day=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		self.delete_all_news()
		
		create_date = faker.date_time_between(start_date = "-2y", end_date = "-1y")
		with freeze_time(create_date):
			bulk_create_news(size = 60, school = self.school)

		current_date = timezone.localtime()

		update_date = f"{current_date.year}-{current_date.month}-01 {faker.time()}"
		with freeze_time(update_date) as frozen_time:
			for _ in range(26):
				list_news = faker.random_elements(
					elements = models.News.objects.all(),
					length = faker.random_int(min = 1, max = 4)
				)

				for news in list_news:
					news.description = faker.paragraph()
					news.save()

				frozen_time.tick(delta = datetime.timedelta(days = 1))
					
		search_day = faker.random_int(min = 1, max = 25)
		format_day = set_format_number(search_day)

		past_date = faker.date_time_between(start_date = "-90d", end_date = "-30d")

		past_update_date = f"{past_date.year}-{past_date.month}-{format_day} {faker.time()}"
		with freeze_time(past_update_date):
			list_news = faker.random_elements(
				elements = models.News.objects.all(),
				length = faker.random_int(min = 1, max = 4)
			)

			for news in list_news:
				news.description = faker.paragraph()
				news.save()

		current_month = current_date.month
		current_year= current_date.year

		total_news_by_fulldate = models.News.objects.filter(
			school_id = self.school.id,
			updated__day = search_day,
			updated__month = current_month,
			updated__year = current_year
		).count()

		total_news_by_day = models.News.objects.filter(
			school_id = self.school.id,
			updated__day = search_day
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"updated_year": current_year,
					"updated_month":current_month,
					"updated_day": search_day
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_fulldate)

		#

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"updated_day": search_day}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_day)

	def test_get_news_filter_by_update_month(self):
		"""
			Validar "GET /news?update_month=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		self.delete_all_news()
		
		create_date = faker.date_time_between(start_date = "-2y", end_date = "-1y")
		with freeze_time(create_date):
			bulk_create_news(size = 50, school = self.school)

		updated_date = timezone.localtime()

		with freeze_time(updated_date) as frozen_time:
			list_news = faker.random_elements(
				elements = models.News.objects.all(),
				length = faker.random_int(min = 2, max = 10)
			)

			for news in list_news:
				news.description = faker.paragraph()
				news.save()
		
		past_date = faker.date_between(start_date = "-180d", end_date = "-90d")
		format_month = set_format_number(updated_date.month)

		past_update_date = f"{past_date.year}-{format_month}-{past_date.day} {faker.time()}" 
		with freeze_time(past_update_date) as frozen_time:
			list_news = faker.random_elements(
				elements = models.News.objects.all(),
				length = faker.random_int(min = 2, max = 10)
			)

			for news in list_news:
				news.description = faker.paragraph()
				news.save()

		search_month = updated_date.month
		updated_year = updated_date.year

		total_news_by_year_month = models.News.objects.filter(
			school_id = self.school.id,
			updated__month = search_month,
			updated__year = updated_year
		).count()

		total_news_by_month = models.News.objects.filter(
			school_id = self.school.id,
			updated__month = search_month
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {
					"updated_year": updated_year,
					"updated_month": search_month
				}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_year_month)

		#

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"updated_month": search_month}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_month)

	def test_get_news_filter_by_update_year(self):
		"""
			Validar "GET /news?update_year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		self.delete_all_news()
		
		create_date = faker.date_time_between(start_date = "-10y", end_date = "-5y")
		with freeze_time(create_date):
			bulk_create_news(size = 100, school = self.school)

		list_years = []

		updated_date = faker.date_time_between(start_date = "-4y", end_date = "-2y")
		with freeze_time(updated_date) as frozen_time:
			for _ in range(3):
				list_news = faker.random_elements(
					elements = models.News.objects.all(),
					length = faker.random_int(min = 10, max = 20)
				)

				for news in list_news:
					news.description = faker.paragraph()
					news.save()
				
				current_date = datetime.datetime.now()
				target_time = current_date + relativedelta(years=1)
				delta = target_time - current_date
				frozen_time.tick(delta = delta)

				list_years.append(current_date.year)

		search_year = faker.random_element(elements = list_years)

		total_news_by_year = models.News.objects.filter(
			school_id = self.school.id,
			updated__year = search_year
		).count()

		response = self.client.get(
			self.get_school_news_url(
				school_id = self.school.id,
				query = {"updated_year": search_year}
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_news_by_year)

	def test_get_news_filter_by_update(self):
		"""
			Validar "GET /news?update_*=<...>"
			- Por rango de fecha
			- Después de una fecha
			- Antes de una fecha
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		self.delete_all_news()
		
		create_date = faker.date_time_between(start_date = "-2y", end_date = "-1y")
		with freeze_time(create_date):
			bulk_create_news(size = 40, school = self.school)

		current_year = timezone.localtime().year

		updated_date = f"{current_year}-01-01 {faker.time()}"
		with freeze_time(updated_date) as frozen_time:
			for _ in range(13):
				list_news = faker.random_elements(
					elements = models.News.objects.all(),
					length = faker.random_int(min = 1, max = 5)
				)

				for news in list_news:
					news.description = faker.paragraph()
					news.save()

				current_date = datetime.datetime.now()
				target_time = current_date + relativedelta(months=1)
				delta = target_time - current_date
				frozen_time.tick(delta = delta)

		format_datetime = "%Y-%m-%d %H:%M:%S"

		format_month_after = set_format_number(faker.random_int(min = 1, max = 5))
		format_month_before = set_format_number(faker.random_int(min = 6, max = 12))

		updated_after_string = f"{current_year}-{format_month_after}-01 00:00:00"
		updated_before_string = f"{current_year}-{format_month_before}-30 23:59:59"

		updated_after = timezone.make_aware(
			datetime.datetime.strptime(updated_after_string, format_datetime)
		)
		updated_before = timezone.make_aware(
			datetime.datetime.strptime(updated_before_string, format_datetime)
		)

		test_case = [
			{
				"filter": {
					"updated_after": updated_after_string,
					"updated_before": updated_before_string
				},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					updated__range = (updated_after, updated_before)
				).count()
			},
			{
				"filter": {"updated_after": updated_after_string},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					updated__gte = updated_after
				).count()
			},
			{
				"filter": {"updated_before": updated_before_string},
				"total": models.News.objects.filter(
					school_id = self.school.id,
					updated__lte = updated_before
				).count()
			},
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(
					self.get_school_news_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatus = response.status_code 

				self.assertEqual(responseStatus, 200)
				self.assertEqual(responseJson["count"], case["total"])

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

		self.URL_NEWS_UPDATE = get_detail_news_url(
			id = self.news.id
		)

		self.update_news = {
			"title": faker.text(max_nb_chars = 20),
			"description": faker.paragraph(),
		}

	def test_update_news(self):
		"""
			Validar "PUT/PATCH /news/:id"
		"""
		self.client.force_authenticate(user = self.user_with_update_perm)

		response = self.client.patch(
			self.URL_NEWS_UPDATE,
			self.update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["title"], self.update_news["title"])
		self.assertEqual(responseJson["description"], self.update_news["description"])

		self.update_news.update({
			"status": models.News.TypeStatus.pending
		})

		response = self.client.patch(
			self.URL_NEWS_UPDATE,
			self.update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["status"], self.update_news["status"])


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
					self.URL_NEWS_UPDATE,
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

		news = create_news()

		response = self.client.patch(
			get_detail_news_url(id = news.id),
			self.update_news
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

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = case["user"])

				response = self.client.patch(
					self.URL_NEWS_UPDATE,
					self.update_news
				)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_update_news_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /news/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_NEWS_UPDATE,
			self.update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_news_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /news/:id" por usuario sin autenticación
		"""

		response = self.client.patch(
			self.URL_NEWS_UPDATE,
			self.update_news
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class NewsDeleteAPITest(testcases.NewsDetailUpdateDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.news = create_news(school = self.school)

		self.URL_NEWS_DELETE = get_detail_news_url(
			id = self.news.id
		)

	def test_delete_news(self):
		"""
			Validar "DELETE /news/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_NEWS_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)


	def test_delete_news_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /news/:id" por una noticia que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		news = create_news()

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
				
				response = self.client.delete(self.URL_NEWS_DELETE)

				responseStatus = response.status_code

				self.assertEqual(responseStatus, 403)


	def test_delete_news_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /news/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_NEWS_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_delete_news_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /news/:id" por usuario sin autenticación
		"""

		response = self.client.delete(self.URL_NEWS_DELETE)

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
