from django.urls import reverse

from .utils import testcases

from apps.school import models

from tests import faker
from tests.school.utils import create_news_media


def get_detail_newsmedia_url(id):
	return reverse(
		"management:news-images-detail",
		kwargs = {"pk": id}
	)


class NewsMediaDetailAPITest(testcases.NewsMediaTestCase):
	def setUp(self):
		super().setUp()
		self.newsmedia = create_news_media()

		self.URL_DETAIL_NEWSMEDIA = get_detail_newsmedia_url(
			id = self.newsmedia.id
		)

	def test_detail_newsmedia(self):
		"""
			Validar "GET /news/images/:id" 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.get(
			self.URL_DETAIL_NEWSMEDIA
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.newsmedia.id)

	def test_detail_newsmedia_does_not_exist(self):
		"""
			Generar [Error 404] "GET /news/images/:id" por ID que no existe 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		news_media_id = models.NewsMedia.objects.last().id
		
		wrong_id = faker.random_int(min = news_media_id + 1)
		

		response = self.client.get(
			get_detail_newsmedia_url(id = wrong_id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_detail_newsmedia_without_authentication(self):
		"""
			Generar [Error 401] "GET /news/images/:id" sin autenticación
		"""
		response = self.client.get(
			self.URL_DETAIL_NEWSMEDIA
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class NewsMediaDeleteAPITest(testcases.NewsMediaTestCase):
	def setUp(self):
		super().setUp()
		self.newsmedia = create_news_media()

		self.URL_DETAIL_NEWSMEDIA = get_detail_newsmedia_url(
			id = self.newsmedia.id
		)

	def test_delete_newsmedia(self):
		"""
			Validar "DELETE /news/images/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(
			self.URL_DETAIL_NEWSMEDIA
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_newsmedia_does_not_exist(self):
		"""
			Generar [Error 404] "DELETE /news/images/:id" por ID que no existe 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		news_media_id = models.NewsMedia.objects.last().id
		
		wrong_id = faker.random_int(min = news_media_id + 1)

		response = self.client.delete(
			get_detail_newsmedia_url(id = wrong_id)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_delete_newsmedia_without_user_permissions(self):
		"""
			Generar [Error 403] "DELETE /news/images/:id" por usuario sin permisos
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.delete(
			self.URL_DETAIL_NEWSMEDIA
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_newsmedia_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /news/images/:id" sin autenticación
		"""
		response = self.client.delete(
			self.URL_DETAIL_NEWSMEDIA
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)