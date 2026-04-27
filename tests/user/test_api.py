import unittest

from django.urls import reverse

from apps.user import models
from apps.user.apiv1 import serializers

from tests import faker

from .utils.testcases import(
	UserTestCase
	UserDetailUpdateTestCase
)
from .utils.utils import create_user


def get_detail_user_url(id):
	return reverse("user:user", kwargs = {"pk": id})


class UserDetailAPITest(UserDetailUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_USER_DETAIL = get_detail_user_url(
			id = self.user.id
		)
	
	def test_user_detail(self):
		"""
			Validar "GET /user/:id"
		"""
		self.client.force_authenticate(user = self.user)

		response = self.client.get(self.URL_USER_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson['id'], self.user.id)
		self.assertEqual(responseJson['name'], self.user.name)
		self.assertEqual(responseJson['email'], self.user.email)
		self.assertEqual(responseJson['role'], self.user.role)


	def test_detail_without_user_permission(self):
		"""
			Generar [Error 403] "GET /user/:id" por acceder a la información de otro usuario sin permisos de 'admin'
		"""
		other_user = create_user()
		
		self.client.force_authenticate(user = self.user)
	
		response = self.client.get(
			get_detail_user_url(id = other_user.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_detail_with_no_existent_user(self):
		"""
			Generar [Error] "GET /USER/:id" por acceder a la información de usuario que no existe
		"""
		self.client.force_authenticate(user = self.user)

		other_user_id = 12

		response = self.client.get(
			get_detail_user_url(id = other_user_id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_detail_without_authentication(self):
		"""
			Generar [Error] "GET /USER/:id" sin autenticación
		"""
		response = self.client.get(self.URL_USER_DETAIL)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class UserUpdateAPITest(UserDetailUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_USER_DETAIL = get_detail_user_url(
			id = self.user.id
		)

	def test_update_user(self):
		"""
			Validar "PUT/PATCH /user/:id"
		"""
		update_user = {
			"name": faker.name(),
			"email": faker.email(),
			"is_active": not self.user.is_active
		}
		
		self.client.force_authenticate(user = self.user)

		response = self.client.put(
			self.URL_USER_DETAIL,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertEqual(responseJson["id"], self.user.id)
		self.assertEqual(responseJson["name"], update_user['name'])
		self.assertEqual(responseJson["email"], update_user['email'])
		self.assertEqual(responseJson["is_active"], update_user['is_active'])

		self.assertNotEqual(responseJson["name"], self.user.name)
		self.assertNotEqual(responseJson["email"], self.user.email)
		self.assertNotEqual(responseJson["is_active"], self.user.is_active)


	def test_update_user_with_not_permissions(self):
		"""
			Generar [Error 403] "PUT/PATCH /user/:id" por intentar actualizar la información de otro usuario
		"""
		other_user = create_user()
	
		self.client.force_authenticate(user = self.user)

		update_user = {
			"name": faker.name()
		}

		response = self.client.patch(
			get_detail_user_url(id = other_user.id),
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertNotEqual(self.user.name, update_user['name'])


	def test_update_user_invalid_endpoint(self):
		"""
			Generar [Error 403] "PUT/PATCH /user/:id" por intentar actualizar el password en este endpoint
		"""

		self.client.force_authenticate(user = self.user)

		update_user = {
			"password": faker.password()
		}

		response = self.client.patch(
			self.URL_USER_DETAIL,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
				
		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertFalse(self.user.check_password(update_user["password"]))

		# Para actualizar el password o el role
		# he diseñado para cada una un endpoint distinto
		# con sus respectivos permisos y validaciones


	def test_update_user_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /user/:id" sin autenticación
		"""
		update_user = {
			"name": faker.name()
		}

		response = self.client.patch(
			self.URL_USER_DETAIL,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertNotEqual(self.user.name, update_user['name'])


class UserUpdatePasswordAPITest(UserDetailUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_UPDATE_PASSWORD = self.get_update_password_url(
			id = self.user.id
		)

	def get_update_password_url(self, id):
		return reverse("user:update-password", kwargs = {"pk": id})

	def test_update_password(self):
		"""
			Validar "PATCH /user/:id/password"
		"""
		self.client.force_authenticate(user = self.user)

		password = faker.password(length = models.MIN_LENGTH_PASSWORD + 1)

		update_user = {
			"password": password,
			"password_confirm": password
		}
		
		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.user.refresh_from_db()

		self.assertEqual(responseStatus, 200)
		self.assertTrue(self.user.check_password(update_user['password']))


	def test_update_password_not_match(self):
		"""
			Generar [Error 400] "PATCH /user/:id/password" las contraseña no coinciden
		"""
		self.client.force_authenticate(user = self.user)

		update_user = {
			"password": faker.password(),
			"password_confirm": faker.password()
		}

		error_messages = ["Las contraseñas no coinciden"]

		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['non_field_errors'], error_messages)


	def test_update_password_without_authentication(self):
		"""
			Generar [Error 401] "PATCH /user/:id/password" sin autenticación
		"""
		password = faker.password(length = models.MIN_LENGTH_PASSWORD + 1)

		update_user = {
			"password": password,
			"password_confirm": password
		}

		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update_user
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

		#Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()

		self.assertFalse(self.user.check_password(password))


class UserUpdateResetPasswordAPITest(UserDetailUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_RESET_PASSWORD = self.get_reset_password_url(
			email = self.user.email
		)

	def get_reset_password_url(self, email):
		return reverse("user:reset-password", query={"email": email})

	@unittest.skip("Funcionamiento incompleto")
	def test_reset_password(self):
		"""
			Validar "PATCH /reset/password"
		"""
		response = self.client.patch(self.URL_RESET_PASSWORD)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)


	@unittest.skip("Funcionamiento incompleto")
	def test_reset_password_without_query_params(self):
		"""
			Generar [Error 422] "PATCH /reset/password" por no enviar el email
		"""
		response = self.client.patch(self.URL_RESET_PASSWORD)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 422)

	@unittest.skip("Funcionamiento incompleto")
	def test_reset_password_with_no_existent_user(self):
		"""
			Generar [Error 404] "PATCH /reset/password" por usuario que no existe
		"""
		email = faker.email()

		response = self.client.patch(
			self.get_reset_password_url(email = email)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
