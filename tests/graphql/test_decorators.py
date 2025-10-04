
from django.contrib.auth.models import AnonymousUser

from apps.graphql import decorators, exceptions

from .utils import testcases

class UserAuthenticationTest(testcases.DecoratorTesCase):

	def test_user_authentication(self):
		"""
			Validar que el decorador retorne un valor definido, [None, en este caso]
		"""
		func = decorators.user_authentication(
			lambda user: user.id == self.user.id
		)(
			lambda info: None
		)

		result = func(self.info_mock(user = self.user))

		self.assertIsNone(result)


class LogiRequiredTest(testcases.DecoratorTesCase):

	def test_login_required(self):
		"""
			Validar que el decorador retorne un valor definido, [None, en este caso]
		"""

		func = decorators.login_required(lambda info: None)

		result = func(self.info_mock(self.user))

		self.assertIsNone(result)


	def test_authentication_error(self):
		"""
			Generar un error por no estar autenticado
		"""

		func = decorators.login_required(lambda info: None)

		with self.assertRaises(exceptions.IsAuthenticated):
			result = func(self.info_mock(AnonymousUser()))