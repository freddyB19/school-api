import unittest

from django.contrib import auth
from django.test import TransactionTestCase

from apps.user.commands import commands
from apps.user.models import TypeRole
from apps.user.models import OccupationStaff

from .utils.utils import (
	faker,
	FakerCreateUser,
	create_user
)


class UserCommandsTest(TransactionTestCase):

	def setUp(self):
		self.faker_user = FakerCreateUser()


	def test_command_create(self):
		"""
			Validar función para crear un usuario
		"""
		role_staff = 1

		result = commands.create_user(
			user = {
				"name": self.faker_user.name,
				"email": self.faker_user.email,
				"password": self.faker_user.password
			}
		)

		status = result.status
		user = result.query

		self.assertTrue(status)
		self.assertIsNotNone(user.id)
		self.assertEqual(user.name, self.faker_user.name)
		self.assertEqual(user.email, self.faker_user.email)
		self.assertEqual(user.role, role_staff)

	def test_command_create_with_wrong_name(self):
		"""
			Generar un error al enviar valores incorrectos o no enviar valores a 'user.name'
		"""
		short_name = "Ana"
		long_name = f"{faker.paragraph(nb_sentences = 5)}{faker.paragraph(nb_sentences = 5)}"

		test_cases = [
			{
				"user": {
					"name": short_name,
					"email": self.faker_user.email,
					"password": self.faker_user.password,
				},
				"expect": {
					"status": False,
					"errors": {
						"field": "name",
						"message": "La longitud debe ser entre 4 y 100 caracteres en (name)",
						"details": {
							"input": short_name
						}
					}
				}
			},
			{
				"user": {
					"name": long_name,
					"email": self.faker_user.email,
					"password": self.faker_user.password,
				},
				"expect": {
					"status": False,
					"errors": {
						"field": "name",
						"message": "La longitud debe ser entre 4 y 100 caracteres en (name)",
					}
				}
			},
			{
				"user": {
					"email": self.faker_user.email,
					"password": self.faker_user.password,
				},
				"expect": {
					"status": False,
					"errors": {
						"field": "name",
						"message": "Field required"
					}
				}
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				result = commands.create_user(user = case["user"])

				expect = case.get("expect")

				self.assertEqual(result.status, expect['status'])
				self.assertEqual(
					result.errors[0].field,
					expect['errors']['field']
				)
				self.assertEqual(
					result.errors[0].message, 
					expect['errors']['message']
				)

	def test_command_create_with_existent_email(self):
		"""
			Generar un error por crear un usuario con un email ya registrado
		"""
		EMAIL = "user12@gmail.com"
		user_1 = create_user(email = EMAIL)

		result = commands.create_user(
			user = {
				"name": self.faker_user.name,
				"email": EMAIL,
				"password": self.faker_user.password,
			}
		)

		status = result.status
		errors = result.errors[0]

		self.assertFalse(status)
		self.assertEqual(errors.field, "email")
		self.assertEqual(errors.message, "Ya existe un usuario con este email")


	def test_command_get(self):
		"""
			Validar función para obtener información de un usuario
		"""
		user = create_user()

		result = commands.get_user(pk = user.id)

		status = result.status
		get_user = result.query 

		self.assertTrue(status)
		self.assertEqual(get_user.id, user.id)
		self.assertEqual(get_user.name, user.name)
		self.assertEqual(get_user.email, user.email)

	def test_command_get_does_not_exists_user(self):
		"""
			Intentar obtener la información de un usuario que no existe
		"""
		user_id = 12

		result = commands.get_user(pk = user_id)

		status = result.status
		errors = result.errors[0]

		self.assertFalse(status)
		self.assertEqual(errors.message, f"No existe información para el usuario {user_id}")

	@unittest.expectedFailure
	def test_command_get_without_pk(self):
		"""
			Generar un error al no enviar un valor para 'pk'
		"""

		result = commands.get_user()

		status = result.status
		self.assertFalse(status)

	def test_command_update(self):
		"""
			Validar que se actualice un usuario
		"""
		
		user = create_user()
		old_name = user.name
		old_email = user.email

		update_user = {
			"name": faker.name(),
			"email": faker.email()
		}
		result = commands.change_user(
			update = update_user,
			pk = user.id
		)

		status = result.status
		query = result.query

		self.assertTrue(status)
		self.assertNotEqual(old_email, query['email'])
		self.assertNotEqual(old_name, query['name'])


		old_role = user.role

		update_user = {
			"role": TypeRole.admin
		}
		result = commands.change_user(
			update = update_user,
			pk = user.id
		)

		status = result.status
		query = result.query

		self.assertTrue(status)
		self.assertNotEqual(old_role, query['role'])
	

	def test_command_update_with_wrong_role(self):
		"""
			Generar un error por enviar una opción de 'role' incorrecto
		"""
		user = create_user()
		wrong_role = "superadmin"

		result = commands.change_user(
			update = {"role": wrong_role},
			pk = user.id
		)

		status = result.status
		user_update =  result.errors[0]

		self.assertFalse(status)
		self.assertEqual(user_update.message, f"La opción '{wrong_role}' es incorrecta")

	
	def test_command_update_with_existent_email(self):
		"""
			Genear un error por actualizar el email por una ya existente
		"""
		EMAIL = "user12@gmail.com"
		user = create_user(email = EMAIL)

		result = commands.change_user(
			update = {"email": EMAIL},
			pk = user.id
		)

		status = result.status
		user_update =  result.errors[0]

		self.assertFalse(status)
		self.assertEqual(user_update.message, f"Ya existe un usuario con este email")

	@unittest.expectedFailure
	def test_command_update_without_pk(self):
		"""
			Generar un error por no enviar el pk de un usuario para actualizar
		"""
		user = create_user()

		result = commands.change_user(
			update = {"name": faker.name()},
		)

		self.assertFalse(result.status)


	def test_command_update_password(self):
		"""
			Validar que se actualice el password
		"""
		user = create_user()
		new_password = "abcd1234"
		result = commands.change_password(
			new_password = new_password,
			pk = user.id
		)

		status = result.status

		user.refresh_from_db()

		self.assertTrue(status)
		self.assertTrue(user.check_password(new_password))


	def test_command_update_with_short_password(self):
		"""
			Generar un error por actualizar password con uno muy corto
		"""
		user = create_user()
		short_password = "abcd12"

		result = commands.change_password(
			new_password = short_password,
			pk = user.id
		)

		status = result.status
		errors = result.errors[0]

		self.assertFalse(status)
		self.assertEqual(errors.message, "La contraseña es muy corta, debe ser mayor a 8 caractéres")


	@unittest.expectedFailure
	def test_command_update_password_without_pk(self):
		"""
			Generar un error por no enviar el pk de un usuario para actualizar el password
		"""
		new_password = "abcd1234"
		result = commands.change_password(
			new_password = new_password
		)

		self.assertFalse(result.status)


	def test_command_valid_email(self):
		"""
			Validar si un 'email' está o no registrado
		"""
		user = create_user()

		result = commands.is_valid_email(email = user.email)

		self.assertTrue(result.status)
		self.assertTrue(result.query)

		result = commands.is_valid_email(email = "user12@example.com")

		self.assertTrue(result.status)
		self.assertFalse(result.query)

	@unittest.expectedFailure
	def test_command_valid_email_without_email(self):
		"""
			Generar un error al no enviar un 'email'
		"""

		result = commands.is_valid_email()

		self.assertFalse(result.status)


	def test_command_generate_password(self):
		"""
			Validar genere un string random para ser usado como password
		"""

		result = commands.generate_password()

		new_password = result.query

		self.assertTrue(result.status)
		self.assertTrue(isinstance(new_password, str))
		self.assertEqual(len(new_password), 12)


	def test_command_generate_password_define_size(self):
		"""
			Definiendo el tamaño del password generado
		"""
		password_size = 8

		result = commands.generate_password( size =  password_size)
		new_password = result.query

		self.assertTrue(result.status)
		self.assertTrue(isinstance(new_password, str))
		self.assertEqual(len(new_password), password_size)

	def test_command_get_by_email(self):
		"""
			Validar obtener usuario por su email
		"""
		EMAIL = "user1@example.com"
		user = create_user(email = EMAIL)
		
		result = commands.get_user_by_email(email = EMAIL)

		get_user = result.query

		self.assertTrue(result.status)
		self.assertEqual(get_user.email, user.email)
		self.assertEqual(get_user.id, user.id)

	def test_command_get_by_email_does_not_exist(self):
		"""
			Intenatar obtener un usuario que no existe
		"""

		EMAIL = "user1@example.com"
		result = commands.get_user_by_email(email = EMAIL)

		self.assertFalse(result.status)
		self.assertIsNone(result.query)

	@unittest.expectedFailure
	def test_command_get_by_email_without_send_email(self):
		"""
			Generar un error por no pasar un valor para 'email'
		"""
		
		result = commands.get_user_by_email()





