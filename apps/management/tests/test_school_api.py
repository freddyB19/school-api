import unittest, tempfile

from django.urls import reverse

from PIL import Image

from apps.school.tests.utils.utils import create_school

from .utils.testcases_data import(
	UPDATE_SCHOOL_WITH_WRONG_DATA
)
from .utils.testcases import SchoolUpdateTest

class SchoolUpdateAPITest(SchoolUpdateTest):
	def setUp(self):
		super().setUp()

		self.URL_SCHOOL_UPDATE = self.get_detail_url(id = self.school.id)

	def get_detail_url(self, id):
		return reverse(
			"management:school-detail",
			kwargs={"pk": id}
		)


	def test_update_school(self):
		"""
			Validar "PUT/PATCH /school/:id"
		"""
		self.client.force_authenticate(user = self.user_with_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}

		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertNotEqual(responseJson["name"], self.school.name)
		self.assertNotEqual(responseJson["history"], self.school.history)


	def test_update_school_without_school_permission(self):
		"""
			Generar [Error 403] "PATCH /school" al no tener permiso para actualizar esta escuela
		"""

		self.client.force_authenticate(user = self.user_with_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}

		other_school = create_school()

		response = self.client.patch(
			self.get_detail_url(id = other_school.id),
			update_school
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_school_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /school/:id"  por usuarios sin permisos para crear una noticia
		"""

		self.client.force_authenticate(user = self.user_without_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}
		
		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_school_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /school/:id" por datos invalidos
		"""
		test_cases = UPDATE_SCHOOL_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				self.client.force_authenticate(user = self.user_with_perm)
				response = self.client.patch(
					self.URL_SCHOOL_UPDATE,
					case["update"]
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, case["expect"]["code"])
				self.assertTrue(case["expect"]["field"] in responseJson)


	def test_update_school_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /school/:id" por usuario sin autenticación
		"""

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}
		
		response = self.client.patch(
			self.URL_SCHOOL_UPDATE,
			update_school
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class SchoolUpdateLogoAPITest(SchoolUpdateTest):
	def setUp(self):
		super().setUp()

		self.URL_SCHOOL_UPDATE_LOGO = self.get_upload_image_url(id = self.school.id)

	def get_upload_image_url(self, id):
		return reverse(
			"management:school-upload-image",
			kwargs = {"pk": id}
		)


	@unittest.skip("Esta función aún no está completada")
	def test_update_school_logo(self):
		"""
			Validar "PATCH /school/:id/upload-image"
		"""

		self.client.force_authenticate(user = self.user_with_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as temp_file:
			image = Image.new("RGB", (10, 10))
			image.save(temp_file, format="JPEG")
			temp_file.seek(0)

			response = self.client.patch(
				self.URL_SCHOOL_UPDATE_LOGO,
				{"logo": temp_file},
				format="multipart"
			)


		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertNotEqual(responseJson["logo"], self.school.logo)
