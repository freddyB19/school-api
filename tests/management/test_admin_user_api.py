from django.urls import reverse

from tests.user.utils.utils import create_user

from .utils import testcases


class UserUpdatePermissionsTest(testcases.AdministratorUserTestCase):
	
	def setUp(self):
		super().setUp()

		self.URL_USER_PERMISSIONS = reverse(
			"management:user-permission",
			kwargs={"pk": self.user_role_staff.id}
		)


	def test_update_permission_user(self):
		"""
			Validar "PATCH /administrador/user/:id"
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
			Generar [Error 403] "PATCH /administrador/user/:id" por usuario con role = 'staff'
		"""
		self.client.force_authenticate(user = self.user_role_staff)

		user = create_user(role = 1)

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
			Generar [Error 401] "PATCH /administrador/user/:id" por usuario sin autenticación
		"""
		user = create_user(role = 1)

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
