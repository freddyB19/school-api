import pprint

from django.urls import reverse

from apps.school import models

from tests import faker

from tests.school.utils import bulk_create_cultural_event_media

from .utils import testcases


def get_detail_culturalevent_media_url(pk):
	return reverse(
		"management:culturalevent-image-detail",
		kwargs = {"pk": pk}
	)

class CulturalEventMediaDetailAPITest(testcases.CulturalEventMediaTestCase):
	def setUp(self):
		super().setUp()

		self.cultural_event_media = bulk_create_cultural_event_media(
			size = 1
		)[0]

		self.URL_DETAIL_CULTURAL_EVENT_MEDIA = get_detail_culturalevent_media_url(
			pk = self.cultural_event_media.id
		)

	def test_get_detail_cultural_event_media(self):
		"""
			Validar "GET /culturalevent/image/:id"
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.get(self.URL_DETAIL_CULTURAL_EVENT_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultural_event_media.id)

	def test_get_detail_cultural_event_media_does_not_exist(self):
		"""
			Generar [Error 404] "GET /culturalevent/image/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)
		
		wrong_id = faker.random_int(
			min = models.CulturalEventMedia.objects.last().id + 1
		)

		response = self.client.get(
			get_detail_culturalevent_media_url(pk = wrong_id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_get_detail_cultural_event_media_without_authentication(self):
		"""
			Generar [Error 401] "GET /culturalevent/image/:id" sin autenticar
		"""

		response = self.client.get(self.URL_DETAIL_CULTURAL_EVENT_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class CulturalEventMediaDeleteAPITest(testcases.CulturalEventMediaTestCase):
	def setUp(self):
		super().setUp()

		self.cultural_event_media = bulk_create_cultural_event_media(
			size = 1
		)[0]
		
		self.URL_DELETE_CULTURAL_EVENT_MEDIA = get_detail_culturalevent_media_url(
			pk = self.cultural_event_media.id
		)

	def test_delete_cultural_event_media(self):
		"""
			Validar "DELETE /culturalevent/image/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_DELETE_CULTURAL_EVENT_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_cultural_event_media_without_user_permission(self):
		"""
			Generar [Error 401] "GET /culturalevent/image/:id" por usuario sin permiso
		"""

		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.delete(self.URL_DELETE_CULTURAL_EVENT_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_cultural_event_media_does_not_exist(self):
		"""
			Generar [Error 404] "DELETE /culturalevent/image/:id" por ID que no existe
		"""

		self.client.force_authenticate(user = self.user_with_delete_perm)
		
		wrong_id = faker.random_int(
			min = models.CulturalEventMedia.objects.last().id + 1
		)

		response = self.client.delete(
			get_detail_culturalevent_media_url(pk = wrong_id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_delete_cultural_event_media_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /culturalevent/image/:id" sin autenticar
		"""

		response = self.client.delete(self.URL_DELETE_CULTURAL_EVENT_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
