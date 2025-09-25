import unittest

from apps.user import models

from tests import faker

from .utils.utils import create_user

from .utils.testcases import UserModelTestCase

class UserModelTest(UserModelTestCase):

	def setUp(self):

		self.data_user = {
			"name": faker.name(),
			"email": faker.email(),
			"role": faker.random_element(elements = (
				models.TypeRole.admin, 
				models.TypeRole.staff
			)),
			"password": faker.pystr(max_chars = models.MIN_LENGTH_PASSWORD + 1)
		}
	
	def test_user(self):
		"""
			Creando un usuario con los datos correctos
		"""
		user = models.User(**self.data_user)
		user.full_clean()
		user.save()

		self.assertEqual(user.name , self.data_user["name"])
		self.assertEqual(user.email , self.data_user["email"])
		self.assertEqual(user.role , self.data_user["role"])

	@unittest.expectedFailure
	def test_create_user_without_email(self):
		"""
			Creando un usuario sin 'email'
		"""
		self.data_user.pop("email")

		user = models.User(**self.data_user)

		user.full_clean()
		user.save()

	@unittest.expectedFailure
	def test_create_user_with_existent_email(self):
		"""
			Creando un usuario con un email ya existente
		"""
		EMAIL = faker.email()
		create_user(email = EMAIL)

		self.data_user.update({"email": EMAIL})

		user = models.User(**self.data_user)

		user.full_clean()
		user.save()


	def test_user_without_role(self):
		"""
			Creando un usuario con sin un 'role'
		"""
		self.data_user.pop("role")

		user = models.User(**self.data_user)

		user.full_clean()
		user.save()

		self.assertEqual(user.role , models.TypeRole.staff.value)

	@unittest.expectedFailure
	def test_user_with_wrong_role(self):
		"""
			Creando un usuario con un role incorrecto
		"""
		wrong_role = 45

		self.data_user.update({"role": wrong_role})

		user = models.User(**self.data_user)

		user.full_clean()
		user.save()
	

	@unittest.expectedFailure
	def test_user_without_password(self):
		"""
			Creando un usuario sin 'password'
		"""
		self.data_user.pop("password")

		user = models.User(**self.data_user)

		user.full_clean()
		user.save()

