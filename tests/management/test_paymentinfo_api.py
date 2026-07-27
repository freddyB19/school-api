import tempfile

from PIL import Image

from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import create_school, bulk_create_payment_info
from tests.user.utils import create_user, get_permissions

from .utils import testcases


def get_create_list_paymentinfo_url(school_id, **extra):
	return reverse(
		"management:paymentinfo-list-create",
		kwargs = {"pk": school_id},
		**extra
	)


class PaymentInfoCreateAPITest(testcases.PaymentInfoCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_PAYMENTINFO_CREATE = get_create_list_paymentinfo_url(
			school_id = self.school.id
		)

		self.add_payment_info = {
			"description": faker.paragraph()
		}

	def test_create_payment_info(self):
		"""
			Validar "POST /payment-info"
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})

			response = self.client.post(
				self.URL_PAYMENTINFO_CREATE,
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertEqual(responseJson["description"], self.add_payment_info["description"])
			
			if self.add_payment_info["media"]:
				total_media = len(self.add_payment_info["media"])

				self.assertTrue(responseJson["media"])
				self.assertEqual(len(responseJson["media"]), total_media)


	def test_create_payment_info_without_description(self):
		"""
			Validar "POST /payment-info" sin descripción
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})
			self.add_payment_info.pop("description")

			response = self.client.post(
				self.URL_PAYMENTINFO_CREATE,
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertIsNone(responseJson["description"])
			
			if self.add_payment_info["media"]:
				total_media = len(self.add_payment_info["media"])

				self.assertTrue(responseJson["media"])
				self.assertEqual(len(responseJson["media"]), total_media)

	def test_create_payment_info_without_media(self):
		"""
			Generar [Error 400] "POST /payment-info" por no enviar archivos de imagen
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_PAYMENTINFO_CREATE,
			self.add_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

		self.add_payment_info.update({"media": []})

		response = self.client.post(
			self.URL_PAYMENTINFO_CREATE,
			self.add_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_create_payment_info_without_school_permission(self):
		"""
			Generar [Error 403] "POST /payment-info" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})

			response = self.client.post(
				get_create_list_paymentinfo_url(
					school_id = other_school.id
				),
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_payment_info_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /payment-info" por usuario que no pertenece a la administración de la escuela
		"""
		
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = [
				"add_paymentinfo"
			])
		)

		self.client.force_authenticate(user = user)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})

			response = self.client.post(
				self.URL_PAYMENTINFO_CREATE,
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_payment_info_without_user_permission(self):
		"""
			Generar [Error 403] "POST /payment-info" por usuario sin permiso
		"""

		self.client.force_authenticate(self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})

			response = self.client.post(
				self.URL_PAYMENTINFO_CREATE,
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_payment_info_without_authentication(self):
		"""
			Generar [Error 401] "POST /payment-info" sin autenticar
		"""

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_payment_info.update({"media": [ntf]})

			response = self.client.post(
				self.URL_PAYMENTINFO_CREATE,
				self.add_payment_info,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 401)


class PaymentInfoListAPITest(testcases.PaymentInfoTestCase):
	def setUp(self):
		super().setUp()

		self.URL_PAYMENTINFO_LIST = get_create_list_paymentinfo_url(
			school_id = self.school.id
		)

		bulk_create_payment_info(size  = 8, school = self.school )
		
	def test_get_payment_info(self):
		"""
			Validar "GET /paymentinfo"
		"""

		self.client.force_authenticate(user = self.user_with_all_perm)

		total_payment_info = models.PaymentInfo.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_PAYMENTINFO_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_payment_info)

	def test_get_payment_info_without_school_permission(self):
		"""
			Generar [Error 403] "GET /paymentinfo" e escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_create_list_paymentinfo_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_payment_info_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /paymentinfo" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ['view_paymentinfo'])
		)

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_PAYMENTINFO_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_payment_info_without_authentication(self):
		"""
			Generar [Error 403] "GET /paymentinfo" sin autenticar
		"""
		response = self.client.get(self.URL_PAYMENTINFO_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)
