import unittest

from django.urls import reverse
from django.test import (
	TestCase,
	TransactionTestCase
)

from rest_framework.test import (
	APIClient,
	force_authenticate
)

from apps.user import models
from apps.user.apiv1 import views

from .utils.utils import (
	faker,
	FakerCreateUser,
	create_user
)


class UserAPITest(TransactionTestCase):
	#serialized_rollback = True
	
	def setUp(self):
		self.client = APIClient()
		self.faker_data = FakerCreateUser()
		self.email = "user12@example.com"
		self.password = "12345678"
		self.user = create_user(email = self.email, password = self.password)
	
		self.adminUser = create_user(
			email = faker.email(), 
			password = faker.pystr_format(),
			role = 0,
		)

		self.URL_REGISTER = reverse("user:register")
		self.URL_LOGIN = reverse("user:login")
		self.URL_USER = reverse("user:user", kwargs = {"pk": self.user.id})
		self.URL_UPDATE_PASSWORD = reverse("user:update-password", kwargs = {"pk": self.user.id})
		self.URL_NAME_UPDATE_ROLE = "user:update-role"
		self.URL_RESET_PASSWORD = reverse("user:reset-password", query={"email": self.user.email})

	def test_create_user(self):
		"""
			Validar que se cree un usuario
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"name": self.faker_data.name,
				"email": self.faker_data.email,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password,
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertEqual(responseJson['name'], self.faker_data.name)
		self.assertEqual(responseJson['email'], self.faker_data.email)
		self.assertEqual(responseJson['role'], 1)

	def test_create_user_with_short_name(self):
		"""
			Creando un usuario un nombre muy corto
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"name": self.faker_data.name[:2],
				"email": self.faker_data.email,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['name'], ["El nombre es muy corto"])

	def test_create_user_with_long_name(self):
		"""
			Creando un usuario un nombre muy largo
		"""
		long_name = f"{faker.paragraph(nb_sentences = 5)}{faker.paragraph(nb_sentences = 5)}"

		response = self.client.post(
			self.URL_REGISTER,
			{
				"name": long_name,
				"email": self.faker_data.email,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['name'], ["El nombre de usuario es muy largo"])
	
	def test_create_user_without_name(self):
		"""
			Creando un usuario sin enviar un nombre
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"email": self.faker_data.email,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password
			}, 	
		)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['name'], ['Debe enviar un nombre para el usuario'])
	
	def test_create_user_with_existent_email(self):
		"""
			Creando un nuevo usuario con un correo ya registrado
		"""
		email = "usuario12@example.com"
		create_user(email = email)

		response = self.client.post(
			self.URL_REGISTER,
			{
				"name": self.faker_data.name,
				"email": email,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password,
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['email'], ["Ya existe un usuario con este email"])
	
	def test_create_user_without_email(self):
		"""
			Creando un usuario sin email
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"name": self.faker_data.name,
				"password": self.faker_data.password,
				"password_confirm": self.faker_data.password
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['email'], ["Debe enviar un email para el usuario"])
	
	def test_create_user_with_wrong_password(self):
		"""
			Creando un usuario con un 'password' diferente al 'password_confirm'
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"email": self.faker_data.email,
				"name": self.faker_data.name,
				"password": self.faker_data.password,
				"password_confirm": "1234"
			}, 	
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['non_field_errors'], ["Las contraseñas no coinciden"])

	def test_create_user_without_password_confirm(self):
		"""
			Creando un usuario sin enviar el 'password_confirm'
		"""
		response = self.client.post(
			self.URL_REGISTER,
			{
				"email": self.faker_data.email,
				"name": self.faker_data.name,
				"password": self.faker_data.password
			}
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['password_confirm'], ["Debe enviar un password de confirmación"])


	def test_login(self):
		"""
			Validar que el usuario puede hacer login
		"""
		response = self.client.post(
			self.URL_LOGIN,
			{
				"email": self.email,
				"password": self.password
			}
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["user"]['id'], self.user.id)
		self.assertEqual(responseJson["user"]['name'], self.user.name)
		self.assertEqual(responseJson["user"]['email'], self.user.email)
		self.assertIn("token", responseJson)
		self.assertIn("access", responseJson['token'])
		self.assertIn("refresh", responseJson['token'])


	def test_login_with_wrong_credentials(self):
		"""
			Generar un error por enviar credenciales invalidas
		"""
		test_case = [
			{"email": self.email, "password": "abcdefgh"},
			{"email": "user67_@example.com", "password": self.password}
		]

		for case in test_case:
			with self.subTest(case  = case):
				response = self.client.post(
					self.URL_LOGIN,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 401)
				self.assertEqual(responseJson, {"errors": {"message": "Credenciales invalidas"}})

	
	def test_user_detail(self):
		"""
			Validar obtener el detalle de un usuario
		"""
		self.client.force_authenticate(user = self.user)

		response = self.client.get(
			self.URL_USER
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson['id'], self.user.id)
		self.assertEqual(responseJson['name'], self.user.name)
		self.assertEqual(responseJson['email'], self.user.email)
		self.assertEqual(responseJson['role'], self.user.role)


	def test_detail_user_with_no_permissions(self):
		"""
			Intentnado acceder a la información de otro usuario sin permisos de 'admin'
		"""
		other_user = create_user()
		
		self.client.force_authenticate(user = self.user)

		response = self.client.get(
			reverse("user:user", kwargs = {"pk": other_user.id})
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		self.assertEqual(responseJson['detail'], "No tienes los permisos suficientes para acceder a esta información")


	def test_user_detail_with_no_existent_user(self):
		"""
			Intentando acceder a la información de usuario que no existe
		"""
		self.client.force_authenticate(user = self.user)

		response = self.client.get(
			reverse("user:user", kwargs = {"pk": 12})
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_user_detail_without_authentication(self):
		"""
			Intentando acceder a la información de usuario sin autenticación
		"""
		response = self.client.get(
			self.URL_USER
		)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


	def test_update_user(self):
		"""
			Validar actualizar [email | name | is_active] en el usuario
		"""
		ocuppations = models.ManagerOcuppation.get()

		update = {
			"name": faker.name(),
			"email": faker.email(),
			"is_active": not self.user.is_active
		}
		
		self.client.force_authenticate(user = self.user)

		response = self.client.put(
			self.URL_USER,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertEqual(responseJson["id"], self.user.id)
		self.assertEqual(responseJson["name"], update['name'])
		self.assertEqual(responseJson["email"], update['email'])
		self.assertEqual(responseJson["is_active"], update['is_active'])

		self.assertNotEqual(responseJson["name"], self.user.name)
		self.assertNotEqual(responseJson["email"], self.user.email)
		self.assertNotEqual(responseJson["is_active"], self.user.is_active)

	def test_update_user_with_not_permissions(self):
		"""
			Intendo actualizar la información de otro usuario
		"""
		other_user = create_user()
	
		update = {
			"name": faker.name()
		}

		self.client.force_authenticate(user = self.user)

		response = self.client.put(
			reverse("user:user", kwargs = {"pk": other_user.id}),
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		self.assertEqual(responseJson['detail'], 'No tienes los permisos suficientes para acceder a esta información')

		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertNotEqual(self.user.name, update['name'])



	def test_update_user_invalid_columns(self):
		"""
			Intentanto actualizar el password en este endpoint
		"""
		roles = models.ManagerRole.get()

		update = {
			"password": "1234abcdf"
		}
		self.client.force_authenticate(user = self.user)

		response = self.client.put(
			self.URL_USER,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		self.assertEqual(responseJson['detail'], "Esta operación no se puede realizar este tipo de cambios: [role | password]")
		
		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertFalse(self.user.check_password(update["password"]))

		# Para actualizar el password o el role
		# he diseñado para cada una un endpoint distinto
		# con sus respectivos permisos y validaciones

	def test_update_user_without_authentication(self):
		"""
			Intendo actualizar la información de un usuario sin autenticación
		"""
		update = {
			"name": faker.name()
		}

		response = self.client.put(
			self.URL_USER,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

		# Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()
		self.assertNotEqual(self.user.name, update['name'])


	def test_update_password(self):
		"""
			Validar actualizar el password del usuario
		"""
		update = {
			"password": "abcdefgh",
			"password_confirm": "abcdefgh"
		}
		
		self.client.force_authenticate(user = self.user)

		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.user.refresh_from_db()

		self.assertEqual(responseStatus, 200)
		self.assertTrue(self.user.check_password(update['password']))


	def test_update_password_dont_match(self):
		"""
			Generar un error por que las contraseña no coinciden
		"""

		update = {
			"password": "abcdefgh",
			"password_confirm": "12345678"
		}

		self.client.force_authenticate(user = self.user)

		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code


		self.assertEqual(responseStatus, 400)
		self.assertEqual(responseJson['non_field_errors'], ["Las contraseñas no coinciden"])


	def test_update_password_without_authentication(self):
		"""
			Intentar actualizar el 'password' sin enviar un token de autenticación
		"""

		update = {
			"password": "abcdefgh",
			"password_confirm": "abcdefgh"
		}

		response = self.client.patch(
			self.URL_UPDATE_PASSWORD,
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

		#Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()

		self.assertTrue(self.user.check_password(self.password))

	
	def test_reset_password(self):
		"""
			Validar que restablecido el password del usuario
		"""
		response = self.client.patch(self.URL_RESET_PASSWORD)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)


	def test_reset_password_without_query_params(self):
		"""
			Intentar acceder al endpoint sin el parametro de busqueda
		"""
		response = self.client.patch(
			reverse("user:reset-password")
		)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 422)


	def test_reset_password_with_no_existent_user(self):
		"""
			Intentar restablecer el password de un usuario que no existe
		"""
		email = "campos_12@example.com"
		response = self.client.patch(
			reverse("user:reset-password", query={"email": email})
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_update_role(self):
		"""
			Intentanto actualizar el role de un usuario
		"""
		roles = models.ManagerRole.get()
		update = {
			"role": roles.admin
		}

		self.client.force_authenticate(user = self.adminUser)

		response = self.client.patch(
			reverse(self.URL_NAME_UPDATE_ROLE, kwargs = {"pk": self.user.id}),
			update
		)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.user.id)
		self.assertNotEqual(responseJson["role"], self.user.role)


	def test_update_role_without_role_admin(self):
		"""
			Intentando actualizar el role de un usuario sin permisios de 'admin'
		"""
		roles = models.ManagerRole.get()
		user = create_user() #usuario con role - staff

		update = {
			"role": roles.admin
		}

		self.client.force_authenticate(user = self.user) #usuario con role - staff

		response = self.client.patch(
			reverse(self.URL_NAME_UPDATE_ROLE, kwargs = {"pk": user.id}),
			update
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		
		#Comprobamos que no se realizaron los cambios
		self.user.refresh_from_db()

		self.assertEqual(self.user.role, roles.staff)


	def test_update_my_own_role(self):
		"""
			Intentar actualizar mi propio role de admin a staff
		"""
		roles = models.ManagerRole.get()
		update = {
			"role": roles.staff
		}

		self.client.force_authenticate(user = self.adminUser)

		response = self.client.patch(
			reverse(self.URL_NAME_UPDATE_ROLE, kwargs = {"pk": self.adminUser.id}),
			update
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
		
		#Comprobamos que no se realizaron los cambios
		self.adminUser.refresh_from_db()

		self.assertEqual(self.adminUser.role, roles.admin)


	def test_update_role_without_authentication(self):
		"""
			Intentar actualizar el role de un usuario sin autenticación
		"""
		roles = models.ManagerRole.get()

		update = {
			"role": roles.admin
		}

		response = self.client.patch(
			reverse(self.URL_NAME_UPDATE_ROLE, kwargs = {"pk": self.user.id}),
			update
		)
		
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


	def tets_delete_user(self):
		"""
			Validar eliminar cuenta de un usuario
		"""
		self.client.force_authenticate(user = self.adminUser)

		response = self.client.delete(self.URL_USER)


		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)


	def tets_delete_user_without_permissions(self):
		"""
			Intentar eliminar un usuario no siendo 'admin'
		"""
		self.client.force_authenticate(user = self.user)

		response = self.client.delete(self.URL_USER)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
