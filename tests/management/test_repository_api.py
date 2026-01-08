import tempfile, random
from datetime import timedelta, datetime

from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta 

from apps.school import models

from freezegun import freeze_time

from tests import faker

from tests.school.utils import (
	create_school,
	create_repository,
	bulk_create_repository
)

from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data, list_upload_files

def get_list_create_repository_url(school_id,**extra):
	return reverse(
		"management:repository-list-create",
		kwargs={"pk": school_id},
		**extra
	)

def get_detail_repository(id):
	return reverse(
		"management:repository-detail",
		kwargs={"pk": id},

	)

class RepositoryCreateAPITest(testcases.RepositoryCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_REPOSITORY_CREATE = get_list_create_repository_url(
			school_id = self.school.id
		)

		self.add_repository = {
			"name_project": faker.text(max_nb_chars = models.MAX_LENGTH_REPOSITORY_NAME_PROJECT),
			"description": faker.paragraph()
		}

	def test_create_repository(self):
		"""
			Validar "POST /repository"
		"""	
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".pdf") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_repository.update({"media": [ntf]})

			response = self.client.post(
				self.URL_REPOSITORY_CREATE,
				self.add_repository,
				format="multipart"
			)

			responseJson = response.data
			responseStatusCode = response.status_code

			self.assertEqual(responseStatusCode, 201)
			self.assertEqual(responseJson["name_project"], self.add_repository["name_project"])
			self.assertEqual(responseJson["description"], self.add_repository["description"])
			self.assertEqual(len(responseJson["media"]), len(self.add_repository["media"]))

	def test_create_repository_without_description(self):
		"""
			Validar "POST /repository" (sin descripción)
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		self.add_repository.pop("description")

		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(responseJson["name_project"], self.add_repository["name_project"])
		self.assertIsNone(responseJson["description"])

	def test_create_repository_without_files(self):
		"""
			Validar "POST /repository" (sin archivos)
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		total_media = 0

		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(responseJson["name_project"], self.add_repository["name_project"])
		self.assertEqual(responseJson["description"], self.add_repository["description"])
		self.assertEqual(len(responseJson["media"]), total_media)

	def test_create_repository_with_data_already_exists(self):
		"""
			Generar [Error 400] "POST /repository" por enviar datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		repository = create_repository(school = self.school)

		self.add_repository.update({"name_project": repository.name_project})

		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

	def test_create_repository_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /repository" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_case = testcases_data.CREATE_REPOSITORY_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.post(
					self.URL_REPOSITORY_CREATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)
		
	def test_create_repository_without_school_permission(self):
		"""
			Generar [Error 403] "POST /repository" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			get_list_create_repository_url(school_id = other_school.id),
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)


	def test_create_repository_without_user_permission(self):
		"""
			Generar [Error 403] "POST /repository" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_repository_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /repository" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["add_repository"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_repository_without_authentication(self):
		"""
			Generar [Error 401] "POST /repository" sin autenticación
		"""
		response = self.client.post(
			self.URL_REPOSITORY_CREATE,
			self.add_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryListAPITest(testcases.RepositoryTestCase):
	def setUp(self):
		super().setUp()

		bulk_create_repository(size = 10, school = self.school)

		self.URL_REPOSITORY_LIST = get_list_create_repository_url(
			school_id = self.school.id
		)

	def test_get_repository(self):
		"""
			Validar "GET /repository"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_repositories = models.Repository.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_REPOSITORY_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repositories)

	def test_get_repository_filter_by_name_project(self):
		"""
			Validar "GET /repository?project=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		name_project = faker.word()

		create_repository(
			school = self.school, 
			name_project = f"{faker.text(max_nb_chars = 15)} {name_project}" 
		)
		create_repository(
			school = self.school, 
			name_project = f"{name_project} {faker.text(max_nb_chars = 15)}" 
		)

		total_repositories = models.Repository.objects.filter(
			school_id = self.school.id,
			name_project__icontains = name_project
		).count()


		response = self.client.get(
			get_list_create_repository_url(
				school_id = self.school.id,
				query={"project": name_project}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repositories)

	def test_get_repository_filter_by_created_range(self):
		"""
			Validar "GET /repository?created_after=<...>&created_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		created_date = f"{current_year}-01-01 12:30:00"
		with freeze_time(created_date) as frozen_time:
			for month in range(1, 13):
				repositories = bulk_create_repository(
					size = faker.random_int(min = 1, max = 5),
					school = self.school
				)

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)
				
		created_start_string = f"{current_year}-{faker.random_int(min = 1, max = 5)}-01 00:00:00"
		created_end_string = f"{current_year}-{faker.random_int(min = 6, max = 12)}-30 23:59:59"

		format_datetime = "%Y-%m-%d %H:%M:%S"
		
		created_start = timezone.make_aware(
			datetime.strptime(created_start_string, format_datetime)
		)
		created_end = timezone.make_aware(
			datetime.strptime(created_end_string, format_datetime)
		)
	
		total_repos = models.Repository.objects.filter(
			school_id = self.school.id,
			created__range = (created_start, created_end)
		).count()

		response = self.client.get(
			get_list_create_repository_url(
				school_id = self.school.id,
				query = {
					"created_after": created_start_string,
					"created_before": created_end_string
				}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repos)

	def test_get_repository_filter_by_created_after_or_before_date(self):
		"""
			Validar "GET /repository?created_after=<...> | ?created_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		current_year = timezone.localtime().year

		created_date = f"{current_year}-01-01 12:30:00"
		with freeze_time(created_date) as frozen_time:
			for _ in range(1, 13):
				bulk_create_repository(
					size = faker.random_int(min = 1, max = 5),
					school = self.school
				)

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		format_datetime = "%Y-%m-%d %H:%M:%S"

		created_after_string = f"{current_year}-{faker.random_int(min = 1, max = 5)}-01 00:00:00"

		created_before_string = f"{current_year}-{faker.random_int(min = 6, max = 12)}-30  23:59:59"

		created_after = timezone.make_aware(
			datetime.strptime(created_after_string, format_datetime)
		)
		created_before = timezone.make_aware(
			datetime.strptime(created_before_string, format_datetime)
		)
			
		test_case = [
			{
				"filter": {"created_after": created_after_string},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					created__gte = created_after
				).count()
			},
			{
				"filter": {"created_before": created_before_string},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					created__lte = created_before
				).count()
			}
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(
					get_list_create_repository_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 200)
				self.assertEqual(responseJson["count"], case["total"])

	def test_get_repository_filter_by_created_month_or_year(self):
		"""
			Validar "GET /repository?created_month=<...> | ?created_year=<...>"
			*Filtra los repositorios de un mes específico definiendo el año.
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		current_year = timezone.localtime().year

		created_date = f"{current_year}-01-01 12:30:00"
		with freeze_time(created_date) as frozen_time:
			for _ in range(1, 13):
				bulk_create_repository(
					size = faker.random_int(min = 1, max = 5),
					school = self.school
				)

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)


		other_datetime_created = faker.date_between(start_date = "-5y", end_date = "-1y")

		with freeze_time(other_datetime_created):
			for month in range(1, 13):
				bulk_create_repository(
					size = faker.random_int(min = 1, max = 5),
					school = self.school
				)

		created_year = current_year
		created_month = faker.random_int(min = 1, max = 12)
		other_year_created = other_datetime_created.year

		test_case = [
			{
				"filter": {"created_year": created_year},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					created__year = created_year
				).count()
			},
			{
				"filter": {"created_month": created_month, "created_year": created_year},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					created__year = created_year,
					created__month = created_month,
				).count()
			},
			{
				"filter": {"created_year": other_year_created},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					created__year = other_year_created
				).count()
			}
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(
					get_list_create_repository_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 200)
				self.assertEqual(responseJson["count"], case["total"])

	def test_get_repository_filter_by_updated_range(self):
		"""
			Validar "GET /repository?updated_after=<...>&updated_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		bulk_create_repository(size = 20, school = self.school)
		
		current_year = timezone.localtime().year

		updated_date = f"{current_year}-01-01 12:30:00"
		with freeze_time(updated_date) as frozen_time:
			for _ in range(1, 13):
				repositories = faker.random_elements(
					elements = models.Repository.objects.all(),
					length = faker.random_int(min = 1, max = 5)
				)

				for repository in repositories:
					repository.description = faker.paragraph()
					repository.save()

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)


		updated_start_string = f"{current_year}-{faker.random_int(min = 1, max = 5)}-01  00:00:00"
		updated_end_string = f"{current_year}-{faker.random_int(min = 6, max = 12)}-30 23:59:59"

		format_datetime = "%Y-%m-%d %H:%M:%S"

		updated_start = timezone.make_aware(
			datetime.strptime(updated_start_string, format_datetime)
		)
		updated_end = timezone.make_aware(
			datetime.strptime(updated_end_string, format_datetime)
		)
	
		total_repos = models.Repository.objects.filter(
			school_id = self.school.id,
			updated__range = (updated_start, updated_end)
		).count()

		response = self.client.get(
			get_list_create_repository_url(
				school_id = self.school.id,
				query={
					"updated_after": updated_start_string, 
					"updated_before": updated_end_string
				}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repos)

	def test_get_repository_filter_by_updated_after_or_before_date(self):
		"""
			Validar "GET /repository?updated_after=<...> | ?updated_before=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		bulk_create_repository(size = 20, school = self.school)

		format_datetime = "%Y-%m-%d %H:%M:%S"
		
		current_year = timezone.localtime().year

		updated_date = f"{current_year}-01-01 12:30:00"
		with freeze_time(updated_date) as frozen_time:
			for _ in range(1, 13):
				repositories = faker.random_elements(
					elements = models.Repository.objects.all(),
					length = faker.random_int(min = 1, max = 5)
				)

				for repository in repositories:
					repository.description = faker.paragraph()
					repository.save()

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
				
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		format_datetime = "%Y-%m-%d %H:%M:%S"

		updated_after_string = f"{current_year}-{faker.random_int(min = 1, max = 5)}-01 00:00:00"

		updated_before_string = f"{current_year}-{faker.random_int(min = 6, max = 12)}-30 23:59:59"

		updated_after = timezone.make_aware(
			datetime.strptime(f"{updated_after_string}", format_datetime)
		)
		updated_before = timezone.make_aware(
			datetime.strptime(f"{updated_before_string}", format_datetime)
		)

		test_case = [
			{
				"filter": {"updated_after": updated_after_string},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					updated__gte = updated_after,
				).count()
			},
			{
				"filter": {"updated_before": updated_before_string},
				"total": models.Repository.objects.filter(
					school_id = self.school.id,
					updated__lte = updated_before,
				).count()
			},
		]

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.get(
					get_list_create_repository_url(
						school_id = self.school.id,
						query = case["filter"]
					)
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 200)
				self.assertEqual(responseJson["count"], case["total"])

	def test_get_repository_filter_by_updated_month(self):
		"""
			Validar "GET /repository?updated_month=<...>&updated_year=<...>"
			Filtra los repositorios de un mes especifico denifiendo el año.
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		bulk_create_repository(size = 30, school = self.school)

		updated_date = faker.date_between(start_date = "+30d", end_date = "+90d")
		with freeze_time(updated_date) as frozen_time:
			repositories = faker.random_elements(
				elements = models.Repository.objects.all(),
				length = faker.random_int(min = 2, max = 10)
			)

			for repository in repositories:
				repository.description = faker.paragraph()
				repository.save()

				frozen_time.tick(delta = timedelta(days = 1))

		total_repos = models.Repository.objects.filter(
			school_id = self.school.id,
			updated__month = updated_date.month,
			updated__year = updated_date.year
		).count()

		response = self.client.get(
			get_list_create_repository_url(
				school_id = self.school.id,
				query={
					"updated_month": updated_date.month, 
					"updated_year": updated_date.year
				}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repos)

	def test_get_repository_filter_by_updated_year(self):
		"""
			Validar "GET /repository?updated_year=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)
		
		bulk_create_repository(size = 30, school = self.school)

		updated_date = faker.date_between(start_date = "+1y", end_date = "+3y")

		with freeze_time(updated_date) as frozen_time:
			for _ in range(1, 13):
				repositories = faker.random_elements(
					elements = models.Repository.objects.all(),
					length = faker.random_int(min = 1, max = 5)
				)

				for repository in repositories:
					repository.description = faker.paragraph()
					repository.save()

				current_date = datetime.now()

				target_time = current_date + relativedelta(months=1)
			
				delta = target_time - current_date

				frozen_time.tick(delta = delta)

		total_repos = models.Repository.objects.filter(
			school_id = self.school.id,
			updated__year = updated_date.year
		).count()


		response = self.client.get(
			get_list_create_repository_url(
				school_id = self.school.id,
				query={"updated_year": updated_date.year}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_repos)

	def test_get_repository_without_school_permission(self):
		"""
			Generar [Error 403] "GET /repository" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_list_create_repository_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_get_repository_with_wrong_user(self):
		"""
			Generar [Error 400] "GET /repository" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_REPOSITORY_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_get_repository_without_authenticate(self):
		"""
			Generar [Error 401] "GET /repository" sin autenticación
		"""
		response = self.client.get(self.URL_REPOSITORY_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryDetailAPITest(testcases.RepositoryDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.repository = create_repository(school = self.school)

		self.URL_REPOSITORY_DETAIL = get_detail_repository(id = self.repository.id)


	def test_detail_repository(self):
		"""
			Validar "GET /repository/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_REPOSITORY_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.repository.id)
		self.assertEqual(responseJson["name_project"], self.repository.name_project)
		self.assertEqual(responseJson["description"], self.repository.description)
		self.assertEqual(len(responseJson["media"]), self.repository.media.count())

	def test_detail_repository_without_school_permission(self):
		"""
			Generar [Error 403] "GET /repository/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_respository = create_repository()

		response = self.client.get(
			get_detail_repository(id = other_respository.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_detail_repository_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /repository/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_REPOSITORY_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)


	def test_detail_repository_without_authenticate(self):
		"""
			Generar [Error 401] "GET /repository/:id" sin autenticación
		"""
		response = self.client.get(self.URL_REPOSITORY_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryDeleteAPITest(testcases.RepositoryDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		repository = create_repository(school = self.school)

		self.URL_REPOSITORY_DELETE = get_detail_repository(id = repository.id)

	def test_delete_repository(self):
		"""
			Validar "DELETE /repository/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_REPOSITORY_DELETE)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 204)

	def test_delete_repository_without_school_permission(self):
		"""
			Generar [Error 403]  "DELETE /repository/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		repository = create_repository()

		response = self.client.delete(
			get_detail_repository(id = repository.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_repository_without_user_permission(self):
		"""
			Generar [Error 403]  "DELETE /repository/:id" por usuario que no tiene permiso.
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_REPOSITORY_DELETE)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_repository_with_wrong_user(self):
		"""
			Generar [Error 403]  "DELETE /repository/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_repository"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_REPOSITORY_DELETE)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_repository_without_authenticate(self):
		"""
			Generar [Error 401]  "DELETE /repository/:id" sin autenticación
		"""
		response = self.client.delete(self.URL_REPOSITORY_DELETE)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryUpdateAPITest(testcases.RepositoryDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.repository = create_repository(school = self.school)

		self.URL_REPOSITORY_UPDATE = get_detail_repository(
			id = self.repository.id
		)

		self.update_repository = {
			"name_project": faker.text(max_nb_chars = models.MAX_LENGTH_REPOSITORY_NAME_PROJECT),
			"description": faker.paragraph()
		}

		self.partial_repository = {
			"description": faker.paragraph()
		}

	def test_update_repository(self):
		"""
			Validar "PUT/PATCH /repository/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		# PUT /repository/:id

		response = self.client.put(
			self.URL_REPOSITORY_UPDATE,
			self.update_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.repository.id)
		self.assertEqual(
			responseJson["name_project"], 
			self.update_repository["name_project"]
		)
		self.assertEqual(
			responseJson["description"], 
			self.update_repository["description"]
		)

		# PATCH /repository/:id

		response = self.client.patch(
			self.URL_REPOSITORY_UPDATE,
			self.partial_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.repository.id)
		self.assertEqual(
			responseJson["description"], 
			self.partial_repository["description"]
		)


	def test_update_repository_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /repository/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_case = testcases_data.UPDATE_REPOSITORY_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_REPOSITORY_UPDATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

	def test_update_repository_with_data_already_exists(self):
		"""
			Generar [Error 400] "PUT/PATCH /repository/:id" por datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		update_name_project = {
			"name_project": self.repository.name_project
		}

		response = self.client.patch(
			self.URL_REPOSITORY_UPDATE,
			update_name_project
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

	def test_update_repository_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /repository/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		repository = create_repository()

		response = self.client.patch(
			get_detail_repository(id = repository.id),
			self.partial_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_repository_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /repository/:id" por usuarion sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.patch(
			self.URL_REPOSITORY_UPDATE,
			self.partial_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_repository_with_wrong_user(self):
		"""
			Generar [Error 400] "PUT/PATCH /repository/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_repository"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_REPOSITORY_UPDATE,
			self.partial_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_repository_without_authentication(self):
		"""
			Generar [Error 400] "PUT/PATCH /repository/:id" sin autenticación
		"""
		response = self.client.patch(
			self.URL_REPOSITORY_UPDATE,
			self.partial_repository
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryUpdateDeleteFilesAPITest(testcases.RepositoryDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.repository = create_repository(school = self.school)

		self.URL_REPOSITORY_FILES = self.get_detail_repository_files_url(
			id = self.repository.id
		)


	def get_detail_repository_files_url(self, id):
		return reverse(
			"management:repository-files",
			kwargs={"pk": id}
		)

	def test_update_repository_files(self):
		"""
			Validar "PATCH /respository/:id/files"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".pdf") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			update_repository_files = {"media": [ntf]}

			response = self.client.patch(
				self.URL_REPOSITORY_FILES,
				update_repository_files,
				format="multipart"
			)

			responseJson = response.data
			responseStatusCode = response.status_code

			self.assertEqual(responseStatusCode, 202)
			self.assertEqual(responseJson["id"], self.repository.id)

	def test_delete_repository_files(self):
		"""
			Validar "DELETE /respository/:id/files"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		total_repository_files = 0

		self.assertGreater(self.repository.media.count(), total_repository_files)

		response = self.client.delete(self.URL_REPOSITORY_FILES)

		responseStatusCode = response.status_code
		
		repository = models.Repository.objects.get(id = self.repository.id)

		self.assertEqual(responseStatusCode, 204)
		self.assertEqual(total_repository_files, repository.media.count())
