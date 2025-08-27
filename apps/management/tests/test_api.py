import unittest, tempfile

from django.urls import reverse
from django.test import TransactionTestCase

from PIL import Image

from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from apps.user.tests.utils.utils import (
	create_user, 
	create_permissions, 
	get_permissions
)
from apps.school.tests.utils.utils import create_school
from apps.management import models
from apps.management.apiv1 import views

from .utils.utils import get_administrator
from .utils.testcases import UPDATE_SCHOOL_WITH_WRONG_DATA, SchoolUpdateTest


class AdministratorAPITest(TransactionTestCase):

	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1, email = "carlos@example.com")
		self.administrator = get_administrator(school_id = self.school.id)
		self.administrator.users.set([self.user_role_admin, self.user_role_staff])


		self.URL_ADMINISTRATOR = reverse(
			"management:administrator", 
			kwargs={"school_id": self.school.id}
		) 
		self.URL_ADMINISTRATOR_DETAIL = reverse(
			"management:administrator-detail", 
			kwargs={"pk": self.administrator.id}
		)
		

	def test_get_administrator(self):
		"""
			Validar endpoint administrator
		"""

		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertLessEqual(len(responseJson["users"]), 5)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())


	def test_get_administrator_with_no_existent_school(self):
		"""
			Intentar acceder a la información de 'administrator' con un ID de escuela que no existe
		"""
		wrong_school_id = 100
		
		response = self.client.get(reverse(
			"management:administrator", 
			kwargs={"school_id": wrong_school_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores del portal de un colegio con ID: {wrong_school_id}")


	def test_get_detail_administrator(self):
		"""
			Validar endpoint administrator-detail
		"""

		response = self.client.get(self.URL_ADMINISTRATOR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())
		self.assertEqual(responseJson["school"]["id"], self.school.id)
		self.assertEqual(responseJson["school"]["name"], self.school.name)


	def test_get_detail_administrator_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint administrator-detail
		"""
		wrong_id = 120
		
		response = self.client.get(reverse(
			"management:administrator-detail", 
			kwargs={"pk": wrong_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores de este portal con ID: {wrong_id}")
	


class UserUpdatePermissionsTest(TransactionTestCase):
	
	def setUp(self):
		create_permissions()

		self.client = APIClient()

		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1, email = "carlos@example.com")

		create_permissions("Create test", "create_test")
		create_permissions("Read test", "read_test")
		create_permissions("Delete test", "delete_test")
		create_permissions("Update test", "update_test")

		self.URL_USER_PERMISSIONS = reverse(
			"management:user-permission",
			kwargs={"pk": self.user_role_staff.id}
		)


	def test_update_permission_user(self):
		"""
			Actualizar los permisos de un usuario
		"""
		self.client.force_authenticate(user = self.user_role_admin)

		update_user_permissions = {
			"permissions": ["create_test", "update_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			len(responseJson["user_permissions"]),
			len(update_user_permissions["permissions"])
		)


		# Definiendo solo un permiso

		update_user_permissions = {
			"permissions": ["delete_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(
			responseJson["user_permissions"], 
			update_user_permissions["permissions"]
		)


	def test_update_permission_user_without_permission_role(self):
		"""
			Intentando actualizar los permisos de un usuario tendiendo como user.role = 'staff'
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		user = create_user(role = 1, email = "user1@example.com")

		update_user_permissions = {
			"permissions": ["create_test", "delete_test"]
		}

		response = self.client.patch(
			reverse(
				"management:user-permission",
				kwargs={"pk": user.id}
			),
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_update_permission_user_without_authentication(self):
		"""
			Intentando actualizar los permisos de un usuario sin autenticación
		"""
		user = create_user(role = 1, email = "user1@example.com")

		update_user_permissions = {
			"permissions": ["create_test", "delete_test"]
		}

		response = self.client.patch(
			self.URL_USER_PERMISSIONS,
			update_user_permissions
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



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
			Actualizando la información de una escuela
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


	def test_update_school_does_not_exist(self):
		"""
			Actualizando la información de una escuela que no existe
		"""

		self.client.force_authenticate(user = self.user_with_perm)

		update_school = {
			"name": "School test 1",
			"history": "Información sobre la historia de la escuela"
		}

		wrong_id = 12

		response = self.client.patch(
			self.get_detail_url(id = wrong_id),
			update_school
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)

	def test_update_school_without_user_permission(self):
		"""
			Actualizando la información de una escuela sin permiso de usuario
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
			Enviando datos erroneos para actualizar una escuela
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
			Actualizando la información de una escuela sin autenticación del usuario
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


	@unittest.skip("Esta función aun no está completada")
	def test_update_school_logo(self):
		"""
			Actualizando el logo de una escuela
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

