from unittest import mock

from django.contrib.auth.models import AnonymousUser

from graphql import GraphQLError

from apps.graphql import exceptions 

from .utils import testcases


class AuthorizationMiddlewareTest(testcases.AuthorizationMiddlewareTestCase):

	def test_authorization_user(self):
		"""
			Validar la autenticación de un usuario
		"""
		header = {
			self.HEADER_NAME: f"{self.HEADER_PREFIX} {self.token}"
		}

		next_mock = mock.Mock()

		info_mock = self.info_mock(user = AnonymousUser(), header = header)

		self.middleware.resolve(next_mock, None, info_mock)

		next_mock.assert_called_once_with(None, info_mock)

		self.assertEqual(info_mock.context.user.id, self.user.id)


	def test_authorization_user_with_invalid_prefix(self):
		"""
			No autenticar por enviar un prefijo invalido en el 'header'
		"""
		header = {
			self.HEADER_NAME: f"Token {self.token}"
		}

		next_mock = mock.Mock()

		info_mock = self.info_mock(user = AnonymousUser(), header = header)

		self.middleware.resolve(next_mock, None, info_mock)

		next_mock.assert_called_once_with(None, info_mock)

		self.assertIsInstance(info_mock.context.user, AnonymousUser)


	def test_authorization_user_without_header(self):
		"""
			No autenticar por no enviar un 'header'
		"""

		next_mock = mock.Mock()

		info_mock = self.info_mock(user = AnonymousUser())

		self.middleware.resolve(next_mock, None, info_mock)

		next_mock.assert_called_once_with(None, info_mock)

		self.assertIsInstance(info_mock.context.user, AnonymousUser)


	def test_authorization_user_with_invalid_token(self):
		"""
			No autenticar por enviar un token invalido en el 'header'
		"""
		header = {
			self.HEADER_NAME: f"{self.HEADER_PREFIX} invalid"
		}

		next_mock = mock.Mock()

		info_mock = self.info_mock(user = AnonymousUser(), header = header)

		with self.assertRaises(GraphQLError):
			self.middleware.resolve(next_mock, None, info_mock)

		next_mock.assert_not_called()