import tempfile

from django.urls import reverse

from apps.school import models

from tests import faker

from tests.school.utils import create_repository, create_school

from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data, list_upload_files

def get_list_create_repository_url(school_id):
	return reverse(
		"management:repository-list-create",
		kwargs={"pk": school_id}
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
