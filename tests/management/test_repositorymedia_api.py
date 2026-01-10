from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import create_respository_media_file

from .utils import testcases

def get_detail_repository_media(id):
	return reverse(
		"management:repository-file-detail",
		kwargs={"pk": id}
	)


class RepositoryMediaFileDetailAPITest(testcases.RepositoryMediaFileTestCase):
	def setUp(self):
		super().setUp()
		
		self.repository_media = create_respository_media_file()
		self.URL_REPOSITORY_MEDIA_DETAIL = get_detail_repository_media(
			id = self.repository_media.id
		)

	def test_detail_repository_media(self):
		"""
			Validar "GET /repository/file/:id"
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.get(self.URL_REPOSITORY_MEDIA_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.repository_media.id)

	def test_detail_repository_media_does_not_exist(self):
		"""
			Generar [Error 404] "GET /repository/file/:id" por ID que no existe 
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		repository_media_id = models.RepositoryMediaFile.objects.last().id

		wrong_id = faker.random_int(min = repository_media_id + 1)

		response = self.client.get(
			get_detail_repository_media(id = wrong_id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 404)

	def test_detail_repository_media_without_authentication(self):
		"""
			Generar [Error 401] "GET /repository/file/:id" sin autenticación
		"""
		response = self.client.get(self.URL_REPOSITORY_MEDIA_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class RepositoryMediaFileDeleteAPITest(testcases.RepositoryMediaFileTestCase):
	def setUp(self):
		super().setUp()

		self.repository_media = create_respository_media_file()
		self.URL_REPOSITORY_MEDIA_DELETE = get_detail_repository_media(
			id = self.repository_media.id
		)

	def test_delete_repository_media(self):
		"""
			Validar "DELETE /repository/file/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_REPOSITORY_MEDIA_DELETE)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 204)

	def test_delete_repository_media_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /repository/file/:id" por usuario sin permisos
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.delete(self.URL_REPOSITORY_MEDIA_DELETE)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_repository_media_does_not_exit(self):
		"""
			Generar [Error 404] "DELETE /repository/file/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		repository_media_id = models.RepositoryMediaFile.objects.last().id

		wrong_id = faker.random_int(min = repository_media_id + 1)

		response = self.client.delete(
			get_detail_repository_media(id = wrong_id)
		)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 404)

	def test_delete_repository_media_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /repository/file/:id" sin autenticación
		"""
		response = self.client.delete(self.URL_REPOSITORY_MEDIA_DELETE)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)
