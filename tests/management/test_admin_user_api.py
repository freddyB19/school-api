from django.urls import reverse

from apps.user import models

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


class AdminUpdateUserRoleAPITest(testcases.AdministratorUserTestCase):
	def setUp(self):
		super().setUp()

		self.UPDATE_USER_ROLE = self.get_update_role_url(
			user_id = self.user_role_staff.id
		)

	def get_update_role_url(self, user_id):
		return reverse(
			"management:user-role-update",
			 kwargs = {"pk": user_id}
		)

	def test_update_role(self):
		"""
			Validar "PATCH/PUT /administrador/user/:id/role"
		"""

		update = {
			"role": models.TypeRole.admin
		}

		self.client.force_authenticate(user = self.user_role_admin)

		response = self.client.patch(
			self.UPDATE_USER_ROLE,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.user_role_staff.id)
		self.assertNotEqual(responseJson["role"], self.user_role_staff.role)


	def test_update_role_without_role_admin(self):
		"""
			Generar [Error 403]  "PATCH/PUT /administrador/user/:id/role" por no tener permisios de 'admin'
		"""
		user_staff = create_user(role = 1) #usuario con role - staff

		update = {
			"role": models.TypeRole.admin
		}

		self.client.force_authenticate(user = self.user_role_staff) #usuario con role - staff

		response = self.client.patch(
			self.get_update_role_url(user_id = user_staff.id),
			update
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		
		#Comprobamos que no se realizaron los cambios
		user_staff.refresh_from_db()

		self.assertEqual(user_staff.role,  models.TypeRole.staff)


	def test_update_my_own_role(self):
		"""
			Generar [Error 403]  "PATCH/PUT /administrador/user/:id/role" por intentar actualizar mi propio role de admin a staff
		"""

		update = {
			"role": models.TypeRole.staff
		}

		self.client.force_authenticate(user = self.user_role_admin)

		response = self.client.patch(
			self.get_update_role_url(user_id = self.user_role_admin.id),
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		
		#Comprobamos que no se realizaron los cambios
		self.user_role_admin.refresh_from_db()

		self.assertEqual(self.user_role_admin.role, models.TypeRole.admin)


	def test_update_role_without_authentication(self):
		"""
			Generar [Error 401]  "PATCH/PUT /administrador/user/:id/role" por no estar autenticado
		"""

		update = {
			"role": models.TypeRole.admin
		}

		response = self.client.patch(
			self.UPDATE_USER_ROLE,
			update
		)
		
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)