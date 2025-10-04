from unittest import mock

from django.conf import settings
from django.test import TestCase, RequestFactory
from graphql.type.definition import GraphQLResolveInfo

from apps.graphql.middleware import AuthorizationMiddleware

from tests.user.utils import create_user

from .utils import encode_token

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

class AuthorizationMiddlewareTestCase(MiddlewareTestCase):
	def setUp(self):
		super().setUp()
		self.user = create_user()
		self.token = encode_token(user = self.user)
		self.middleware = AuthorizationMiddleware()
		self.HEADER_NAME = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_NAME']
		self.HEADER_PREFIX = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_PREFIX']


class HTTPAuthorizationTestCase(TestCase):
	def setUp(self):
		self.user = create_user()

class GetHTTPAuthorizationTestCase(HTTPAuthorizationTestCase):
	def setUp(self):
		super().setUp()
		self.token = encode_token(user = self.user)
		self.request_factory = RequestFactory()
		self.HEADER_NAME = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_NAME']
		self.HEADER_PREFIX = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_PREFIX']