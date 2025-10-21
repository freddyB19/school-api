import unittest

from rest_framework import exceptions

from apps.user import models
from apps.user.commands import commands
from apps.user.apiv1 import serializers


from tests import faker

from .utils.testcases import (
	CommandGetUserTestCase,
	CommandCreateUserTestCase,
	CommandGetUserByEmailTestCase,
	CommandGeneratePasswordTestCase
)
from .utils.utils import create_user

class CommandCreateUserTest(CommandCreateUserTestCase):
	def setUp(self):
		super().setUp()

		password = faker.password()

		self.new_user = {
			"name": faker.name(),
			"email": faker.email(),
			"password": password,
			"password_confirm": password
		}

	def test_command_create(self):
		"""
			Validar función para crear un usuario
		"""
		serializer = serializers.UserRegisterSerializer(
			data = self.new_user
		)

		serializer.is_valid(raise_exception = True)

		user = serializer.save()

		user_role_staff = models.TypeRole.staff

		self.assertTrue(user.id)
		self.assertEqual(user.name, self.new_user["name"])
		self.assertEqual(user.email, self.new_user["email"])
		self.assertEqual(user.role, user_role_staff)


	def test_command_create_with_wrong_name(self):
		"""
			Generar un error al enviar valores incorrectos a 'user.name'
		"""

		password = faker.password()

		test_cases = [
			{
				"name": faker.pystr(max_chars = models.MIN_LENGTH_NAME - 1),
				"email": faker.email(),
				"password": password,
				"password_confirm": password,

			},
			{
				"name": faker.pystr(max_chars = models.MAX_LENGTH_NAME + 1),
				"email": faker.email(),
				"password": password,
				"password_confirm": password,

			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				serializer = serializers.UserRegisterSerializer(
					data = case
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)


	def test_command_create_with_existent_email(self):
		"""
			Generar un error por crear un usuario con un email ya registrado
		"""
		EMAIL = faker.email()

		create_user(email = EMAIL)

		self.new_user.update({"email": EMAIL})

		serializer = serializers.UserRegisterSerializer(
			data = self.new_user
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)


class CommandGetUserTest(CommandGetUserTestCase):
	def test_command_get(self):
		"""
			Validar función para obtener información de un usuario
		"""

		command = commands.get_user(pk = self.user.id)

		result_user = command.query 

		self.assertTrue(command.status)
		self.assertEqual(result_user.id, self.user.id)
		self.assertEqual(result_user.name, self.user.name)
		self.assertEqual(result_user.email, self.user.email)

	def test_command_get_does_not_exists_user(self):
		"""
			Intentar obtener la información de un usuario que no existe
		"""
		user_id = 12

		command = commands.get_user(pk = user_id)

		self.assertFalse(command.status)
		self.assertTrue(command.errors)
		self.assertIsNone(command.query)


class CommandGeneratePasswordTest(CommandGeneratePasswordTestCase):
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


class CommandGetUserByEmailTest(CommandGetUserByEmailTestCase):
	def test_command_get_by_email(self):
		"""
			Validar obtener usuario por su email
		"""		
		command = commands.get_user_by_email(email = self.EMAIL)

		get_user = command.query

		self.assertTrue(command.status)
		self.assertEqual(get_user.email, self.user.email)
		self.assertEqual(get_user.id, self.user.id)

	def test_command_get_by_email_does_not_exist(self):
		"""
			Intenatar obtener un usuario que no existe
		"""

		email = faker.email()
		command = commands.get_user_by_email(email = email)

		self.assertFalse(command.status)
		self.assertTrue(command.errors)
		self.assertIsNone(command.query)