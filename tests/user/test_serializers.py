from tests import faker

from apps.user import models
from apps.user.apiv1 import serializers

from .utils.testcases import SerializersUserTestCase


class SerializersUserTest(SerializersUserTestCase):

	def setUp(self):
		password = faker.password()
		self.data_new_user = {
			"name": faker.name(),
			"email": faker.email(),
			"password": password,
			"password_confirm": password
		}

	def test_serializer_create_user(self):
		"""
			Validar método para crear usuario del serializador
		"""

		serializer = serializers.UserRegisterSerializer(data = self.data_new_user)

		self.assertTrue(serializer.is_valid())

		new_user = serializer.save()

		self.assertIsInstance(new_user, models.User)
		self.assertIsNotNone(new_user.id)


	def test_serializer_create_user_without_validate_data(self):
		"""
			Usar el método .save() sin validar los datos
		"""
		self.data_new_user.update({
			"name": faker.pystr(max_chars = models.MIN_LENGTH_NAME - 1),
			"password": faker.password(),
			"password_confirm": faker.password()
		})

		serializer = serializers.UserRegisterSerializer(data = self.data_new_user)

		with self.assertRaisesMessage(AssertionError, "You must call `.is_valid()` before calling `.save()`."):
			new_user = serializer.save()

			self.assertIsInstance(new_user, models.User)


	def test_serializer_create_user_with_wrong_data(self):
		"""
			Intentando crear al usuario con datos invalidos
		"""

		self.data_new_user.update({
			"name": faker.pystr(max_chars = models.MIN_LENGTH_NAME - 1),
			"password": faker.password(),
			"password_confirm": faker.password()
		})

		serializer = serializers.UserRegisterSerializer(data = self.data_new_user)
		
		self.assertFalse(serializer.is_valid())

		with self.assertRaisesMessage(AssertionError, "You cannot call `.save()` on a serializer with invalid data."):
			serializer.save()