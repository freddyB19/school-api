from unittest import mock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from graphql.type.definition import GraphQLResolveInfo

from apps.user.tests.utils.utils import create_user

from apps.graphql import decorators, exceptions


class DecoratorTesCase(TestCase):
	
	def setUp(self):
		self.user = create_user()
		self.request_factory = RequestFactory()

	def info_mock(self, user=None, **kwargs):
		request = self.request_factory.post("/")
		
		if user:
			request.user = user
		
		# Representa los valores que se tomarán en el 'wrapper' del decorador 'context'
		return mock.Mock(
       		context = request,
       		spec = GraphQLResolveInfo,
       		**kwargs
		)


class UserAuthenticationTest(DecoratorTesCase):

	def test_user_authentication(self):
		"""

		"""
		func = decorators.user_authentication(
			lambda user: user.id == self.user.id
		)(
			lambda info: None
		)

		result = func(self.info_mock(user = self.user))

		self.assertIsNone(result)


class LogiRequiredTest(DecoratorTesCase):

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