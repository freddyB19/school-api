from unittest import mock

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from graphql import GraphQLError
from graphql.type.definition import GraphQLResolveInfo

from apps.user.tests.utils.utils import create_user
from apps.graphql.middleware import AuthorizationMiddleware
from apps.graphql import exceptions 

from .utils import encode_token


HEADER_NAME = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_NAME']
HEADER_PREFIX = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_PREFIX']

class MiddlewareTestCase(TestCase):
	def setUp(self):
		self.request_factory = RequestFactory()

	def info_mock(self, user = None, header = None, **kwargs):
		request = self.request_factory.get("/", **(header or {}))

		if user:
			request.user = user

		return mock.Mock(
			context = request,
			spec = GraphQLResolveInfo,
			**kwargs
		)


class AuthorizationMiddlewareTest(MiddlewareTestCase):

	def setUp(self):
		super().setUp()
		self.user = create_user()
		self.token = encode_token(user = self.user)
		self.middleware = AuthorizationMiddleware()

	def test_authorization_user(self):
		"""
			Validar la autenticación de un usuario
		"""
		header = {
			HEADER_NAME: f"{HEADER_PREFIX} {self.token}"
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
			HEADER_NAME: f"Token {self.token}"
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
			HEADER_NAME: f"{HEADER_PREFIX} invalid"
		}

		next_mock = mock.Mock()

		info_mock = self.info_mock(user = AnonymousUser(), header = header)

		with self.assertRaises(GraphQLError):
			self.middleware.resolve(next_mock, None, info_mock)

		next_mock.assert_not_called()