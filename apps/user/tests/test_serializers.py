from django.test import TestCase

from apps.user.apiv1 import serializers
from apps.user.models import User

from .utils.utils import FakerCreateUser


class SerializersTest(TestCase):

	def setUp(self):
		self.faker_user = FakerCreateUser()

	def test_serializer_create_user(self):
		"""
			Validar método para crear usuario del serializador
		"""
		data_new_user = {
			"name": self.faker_user.name,
			"email": self.faker_user.email,
			"password": self.faker_user.password,
			"password_confirm": self.faker_user.password
		}

		serializer = serializers.UserRegisterSerializer(data = data_new_user)

		self.assertTrue(serializer.is_valid())

		new_user = serializer.save()

		self.assertIsInstance(new_user, User)
		self.assertIsNotNone(new_user.id)

	def test_serializer_create_user_without_validate_data(self):
		"""
			Usar el método .save() sin validar los datos
		"""
		short_name = "Ana"
		password = self.faker_user.password
		password_confirm = "asbasd123x_s"

		data_new_user = {
			"name": short_name,
			"email": self.faker_user.email,
			"password": password,
			"password_confirm": password_confirm
		}

		serializer = serializers.UserRegisterSerializer(data = data_new_user)

		with self.assertRaisesMessage(AssertionError, "You must call `.is_valid()` before calling `.save()`."):
			new_user = serializer.save()

			self.assertIsInstance(new_user, User)


	def test_serializer_create_user_with_wrong_data(self):
		"""
			Intentando crear al usuario con datos invalidos
		"""

		short_name = "Ana"
		password = self.faker_user.password
		password_confirm = "asbasd123x_s"

		data_new_user = {
			"name": short_name,
			"email": self.faker_user.email,
			"password": password,
			"password_confirm": password_confirm
		}

		serializer = serializers.UserRegisterSerializer(data = data_new_user)
		
		self.assertFalse(serializer.is_valid())

		with self.assertRaisesMessage(AssertionError, "You cannot call `.save()` on a serializer with invalid data."):
			new_user = serializer.save()

			self.assertIsInstance(new_user, User)
			self.assertIsNotNone(new_user.id)
