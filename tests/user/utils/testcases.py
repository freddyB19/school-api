from django.test import TransactionTestCase, TestCase

from rest_framework.test import APIClient, APITestCase

from tests import faker

from .utils import create_user

class UserModelTestCase(TransactionTestCase):
	pass


class CommandCreateUserTestCase(TransactionTestCase):
	pass


class CommandGetUserTestCase(TransactionTestCase):
	def setUp(self):
		self.user = create_user()


class CommandGeneratePasswordTestCase(TestCase):
	pass


class CommandGetUserByEmailTestCase(TransactionTestCase):
	def setUp(self):
		self.EMAIL = faker.email()
		self.user = create_user(email = self.EMAIL)


class SerializersUserTestCase(TestCase):
	pass


class UserTestCase(APITestCase):
	def setUp(self):
		self.client = APIClient()

class UserDetailUpdateTestCase(UserTestCase):
	def setUp(self):
		super().setUp()

		self.user = create_user()


class UserLoginTestCase(UserTestCase):
	def setUp(self):
		super().setUp()

		self.email = faker.email()
		self.password = faker.password()

		self.user = create_user(email = self.email, password = self.password)

class ServiceTestCase(TestCase):
	pass