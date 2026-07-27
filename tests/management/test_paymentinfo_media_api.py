
import pprint

from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import bulk_create_payment_info_media

from .utils import testcases

def get_detail_payment_info_media_url(pk):
	return reverse(
		"management:paymentinfo-image-detail",
		kwargs={"pk": pk}
	)


class PaymentInfoMediaDetailTest(testcases.PaymentInfoMediaDetailDeleteTestCase):
	def setUp(self):
		super().setUp()

		self.payment_info_media = bulk_create_payment_info_media(
			size = 1
		)[0]

		self.URL_PAYMENTINFO_MEDIA_URL = get_detail_payment_info_media_url(
			pk = self.payment_info_media.id
		)

	def test_get_detail_paymentinfo_media(self):
		"""
			Validar "GET /paymentinfo/image/:id"
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		response = self.client.get(self.URL_PAYMENTINFO_MEDIA_URL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info_media.id)

	def test_get_detail_paymentinfo_media_does_not_exist(self):
		"""
			Generar [Error 404] "GET /paymentinfo/image/:id" por ID que no existe
		"""
		self.client.force_authenticate(user = self.user_with_view_perm)

		wrong_id = faker.random_int(
			min =  models.PaymentInfoMedia.objects.last().id +1
		)

		response = self.client.get(
			get_detail_payment_info_media_url(pk = wrong_id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_detail_paymentinfo_media_without_authentication(self):
		"""
			Generar [Error 401] "GET /paymentinfo/image/:id" sin autenticar
		"""
		response = self.client.get(self.URL_PAYMENTINFO_MEDIA_URL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
