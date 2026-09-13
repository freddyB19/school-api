import tempfile

from PIL import Image

from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import create_school, bulk_create_payment_info, create_payment_info
from tests.user.utils import create_user, get_permissions

from .utils import testcases


def get_create_list_paymentinfo_url(school_id, **extra):
	return reverse(
		"management:paymentinfo-list-create",
		kwargs = {"pk": school_id},
		**extra
	)

def get_detail_paymentinfo_url(pk):
	return reverse(
		"management:paymentinfo-detail",
		kwargs = {"pk": pk}
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


class PaymentInfoDetailAPITest(testcases.PaymentInfoDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.payment_info = create_payment_info(school = self.school)

		self.URL_PAYMENTINFO_DETAIL = get_detail_paymentinfo_url(
			pk = self.payment_info.id
		)

	def test_detail_payment_info(self):
		"""
			Validar "GET /paymentinfo/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_PAYMENTINFO_DETAIL)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info.id)

	def test_detail_payment_info_without_school_permission(self):
		"""
			Generar [Error 403] "GET /paymentinfo/:id" de escuela que no tiene permiso de acceder  
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		payment_info = create_payment_info()

		response = self.client.get(
			get_detail_paymentinfo_url(payment_info.id)
		)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_payment_info_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /paymentinfo/:id" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["view_paymentinfo"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_PAYMENTINFO_DETAIL)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_payment_info_without_authentication(self):
		"""
			Generar [Error 401] "GET /paymentinfo/:id" sin autenticar 
		"""
		response = self.client.get(self.URL_PAYMENTINFO_DETAIL)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class PaymentInfoDeleteAPITest(testcases.PaymentInfoDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.payment_info = create_payment_info(school = self.school)

		self.URL_PAYMENTINFO_DELETE = get_detail_paymentinfo_url(
			pk = self.payment_info.id
		)

	def test_delete_payment_info(self):
		"""
			Validar "DELETE /paymentinfo/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_PAYMENTINFO_DELETE)
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_payment_info_without_school_permission(self):
		"""
			Generar [Error 403]"DELETE /paymentinfo/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		payment_info = create_payment_info()

		response = self.client.delete(
			get_detail_paymentinfo_url(pk = payment_info.id)
		)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_payment_info_without_user_permission(self):
		"""
			Generar [Error 403]"DELETE /paymentinfo/:id" por usuario sin permisos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_PAYMENTINFO_DELETE)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_payment_info_with_wrong_user(self):
		"""
			Generar [Error 403]"DELETE /paymentinfo/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_paymentinfo"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_PAYMENTINFO_DELETE)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_payment_info_without_authentication(self):
		"""
			Generar [Error 401]"DELETE /paymentinfo/:id" sin autenticar
		"""
		response = self.client.delete(self.URL_PAYMENTINFO_DELETE)
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

class PaymentInfoUpdateAPITest(testcases.PaymentInfoDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.payment_info = create_payment_info(school = self.school)

		self.URL_PAYMENTINFO_UPDATE = get_detail_paymentinfo_url(
			pk = self.payment_info.id
		)

		self.update_payment_info = {
			"description": faker.paragraph()
		}


	def test_update_payment_info(self):
		"""
			Validar "PUT/PATCH /paymentinfo/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.put(
			self.URL_PAYMENTINFO_UPDATE,
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info.id)
		self.assertNotEqual(responseJson["description"], self.payment_info.description)

		# Validar "PUT/PATCH /paymentinfo/:id"

		response = self.client.patch(
			self.URL_PAYMENTINFO_UPDATE,
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info.id)
		self.assertNotEqual(responseJson["description"], self.payment_info.description)

	def test_update_payment_info_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /paymentinfo/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.put(
			self.URL_PAYMENTINFO_UPDATE,
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_payment_info_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /paymentinfo/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		payment_info = create_payment_info()

		response = self.client.put(
			get_detail_paymentinfo_url(payment_info.id),
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_payment_info_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /paymentinfo/:id" por usuario que no forma parte de la administración
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_paymentinfo"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_PAYMENTINFO_UPDATE,
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_payment_info_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /paymentinfo/:id" sin autenticar
		"""
		response = self.client.patch(
			self.URL_PAYMENTINFO_UPDATE,
			self.update_payment_info
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class PaymentInfoMediaUpdateDeleteAPITest(testcases.PaymentInfoDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.payment_info = create_payment_info(school = self.school)

		self.URL_PAYMENTINFO_MEDIA_DETAIL = self.get_detail_payment_info_media(
			self.payment_info.id
		)

	def get_detail_payment_info_media(self, pk):
		return reverse(
			"management:paymentinfo-image",
			kwargs = {"pk": pk}
		)

	def test_update_payment_info_image(self):
		"""
			Validar "PATCH /paymentinfo/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			response = self.client.patch(
				self.URL_PAYMENTINFO_MEDIA_DETAIL,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 202)

	def test_delete_all_payment_info_image(self):
		"""
			Validar "DELETE /paymentinfo/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_PAYMENTINFO_MEDIA_DETAIL)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_update_payment_info_media_with_wrong_method(self):
		"""
			Generar [Error] "PATCH /paymentinfo/:id" por método incorrecto
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			response = self.client.put(
				self.URL_PAYMENTINFO_MEDIA_DETAIL,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 405)

	def test_update_payment_info_image_without_user_permission(self):
		"""
			Generar [Error] "PATCH /paymentinfo/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			response = self.client.patch(
				self.URL_PAYMENTINFO_MEDIA_DETAIL,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_update_payment_info_image_without_school_permission(self):
		"""
			Generar [Error] "PATCH /paymentinfo/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		payment_info = create_payment_info()

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			response = self.client.patch(
				self.get_detail_payment_info_media(payment_info.id),
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_delete_all_payment_info_image_without_user_permission(self):
		"""
			Generar [Error] "DELETE /paymentinfo/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_PAYMENTINFO_MEDIA_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_all_payment_info_image_without_school_permission(self):
		"""
			Generar [Error] "DELETE /paymentinfo/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		payment_info = create_payment_info()

		response = self.client.delete(self.get_detail_payment_info_media(
			payment_info.id
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
