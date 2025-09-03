import unittest
from django.test import TransactionTestCase

from apps.user import models

from .utils.utils import create_user
from .utils.utils import FakerCreateUser


class UserModelTest(TransactionTestCase):
	serialized_rollback = True

	def setUp(self):
		self.faker_user =  FakerCreateUser()
	
	def test_user(self):
		"""
			Creando un usuario con los datos correctos
		"""
		user = models.User(
			name = self.faker_user.name,
			email = self.faker_user.email,
			role = self.faker_user.role,
			password = self.faker_user.password
		)
		user.full_clean()
		user.save()

		self.assertEqual(user.name , self.faker_user.name)
		self.assertEqual(user.email , self.faker_user.email)
		self.assertEqual(user.role , self.faker_user.role)

	@unittest.expectedFailure
	def test_create_user_without_email(self):
		"""
			Creando un usuario sin 'email'
		"""
		user = models.User(
			name = self.faker_user.name,
			role = self.faker_user.role,
			password = self.faker_user.password
		)

		user.full_clean()
		user.save()

	@unittest.expectedFailure
	def test_create_user_with_existent_email(self):
		"""
			Creando un usuario con un email ya existente
		"""
		EMAIL = "correo12@example.com"
		user_1 = create_user(email = EMAIL)

		user = models.User(
			name = self.faker_user.name,
			email = EMAIL,
			role = self.faker_user.role,
			password = self.faker_user.password
		)

		user.full_clean()
		user.save()


	def test_user_without_role(self):
		"""
			Creando un usuario con sin un 'role'
		"""
		user = models.User(
			name = self.faker_user.name,
			email = self.faker_user.email,
			role = self.faker_user.role,
			password = self.faker_user.password
		)

		user.full_clean()
		user.save()

		self.assertEqual(user.role , models.TypeRole.staff.value)

	@unittest.expectedFailure
	def test_user_with_wrong_role(self):
		"""
			Creando un usuario con un role incorrecto
		"""
		wrong_role = 45

		user = models.User(
			name = self.faker_user.name,
			email = self.faker_user.email,
			role = 45,
			password = self.faker_user.password
		)

		user.full_clean()
		user.save()
	

	@unittest.expectedFailure
	def test_user_without_password(self):
		"""
			Creando un usuario sin 'password'
		"""
		user = models.User(
			name = self.faker_user.name,
			email = self.faker_user.email,
			role = self.faker_user.role,
		)

		user.full_clean()
		user.save()

