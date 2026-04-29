import pprint

from django.urls import reverse

from apps.school import models

from tests import faker

from tests.school.utils import bulk_create_infraestructure_media

from .utils import testcases


def get_detail_infraestructuremedia_url(pk):
	return reverse(
		"management:infraestructure-image-detail",
		kwargs={"pk": pk},
	)


class InfraestructureMediaDetailAPITest(testcases.InfraestructureMediaTestCase):
	def setUp(self):
		super().setUp()

		self.infraestructure_media = bulk_create_infraestructure_media(
			size = 1
		)[0]

		self.URL_DETAIL_INFRAESTRUCTURE_MEDIA = get_detail_infraestructuremedia_url(
			pk = self.infraestructure_media.id
		)

	def test_get_detail_infraestructure_media(self):
		"""
			Validar "GET /infraestructure/image/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.get(self.URL_DETAIL_INFRAESTRUCTURE_MEDIA)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.infraestructure_media.id)

	def test_get_detail_infraestructure_media_does_not_exit(self):
		"""
			Generar [Error 404] "GET /infraestructure/image/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		wrong_id = faker.random_int(min = self.infraestructure_media.id + 1)

		response = self.client.get(
			get_detail_infraestructuremedia_url(wrong_id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 404)

	def test_get_detail_infraestructure_media_without_authentication(self):
		"""
			Generar [Error 401] "GET /infraestructure/image/:id" sin autenticación
		"""
		response = self.client.get(self.URL_DETAIL_INFRAESTRUCTURE_MEDIA)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class InfraestructureMediaDeleteAPITest(testcases.InfraestructureMediaTestCase):
	def setUp(self):
		super().setUp()

		self.infraestructure_media = bulk_create_infraestructure_media(
			size = 1
		)[0]

		self.URL_DELETE_INFRAESTRUCTURE_MEDIA = get_detail_infraestructuremedia_url(
			pk = self.infraestructure_media.id
		)

	def test_delete_infraestructure_media(self):
		"""
			Validar "DELETE /infraestructure/image/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_DELETE_INFRAESTRUCTURE_MEDIA)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 204)

	def test_delete_infraestructure_media_does_not_exist(self):
		"""
			Generar [Error 404] "DELETE /infraestructure/image/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)
		
		infra_media_id = models.InfraestructureMedia.objects.last().id 
		
		wrong_id = faker.random_int(min = infra_media_id + 1)

		response = self.client.delete(
			get_detail_infraestructuremedia_url(pk = wrong_id )
		)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 404)

	def test_delete_infraestructure_media_without_user_permission(self):
		"""
			Generar [Error 400] "DELETE /infraestructure/image/:id" por usuario sin permisos
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.delete(self.URL_DELETE_INFRAESTRUCTURE_MEDIA)

		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_infraestructure_media_without_authentication(self):
		"""
			Generar [Error 400] "DELETE /infraestructure/image/:id" sin autenticación
		"""

		response = self.client.delete(self.URL_DELETE_INFRAESTRUCTURE_MEDIA)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)
