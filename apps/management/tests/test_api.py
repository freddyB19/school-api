from django.urls import reverse

from apps.user.tests.utils.utils import create_user

from .utils.testcases import AdministratorTest, AdministratorUserTest


class AdministratorAPITest(AdministratorTest):

	def setUp(self):
		super().setUp()

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
		self.client.force_authenticate(user = self.user_role_staff)

		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertLessEqual(len(responseJson["users"]), 5)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())


	def test_get_administrator_does_not_existent_school(self):
		"""
			Intentar acceder a la información de 'administrator' con un ID de escuela que no existe
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		wrong_school_id = 100
		
		response = self.client.get(reverse(
			"management:administrator", 
			kwargs={"school_id": wrong_school_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores del portal de un colegio con ID: {wrong_school_id}")

	def test_get_administrator_without_authentication(self):
		"""
			Accediendo a la información de 'administrator' sin autenticación del usuario
		"""
		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


	def test_get_detail_administrator(self):
		"""
			Validar endpoint administrator-detail
		"""
		self.client.force_authenticate(user = self.user_role_staff)

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
		self.client.force_authenticate(user = self.user_role_staff)

		wrong_id = 120
		
		response = self.client.get(reverse(
			"management:administrator-detail", 
			kwargs={"pk": wrong_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores de este portal con ID: {wrong_id}")
	

	def test_get_detail_administrator_without_authentication(self):
		"""
			Accediendo al endpoint 'administrator-detail' sin autenticación
		"""
		response = self.client.get(self.URL_ADMINISTRATOR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class UserUpdatePermissionsTest(AdministratorUserTest):
	
	def setUp(self):
		super().setUp()

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
