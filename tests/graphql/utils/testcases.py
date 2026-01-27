
from django.conf import settings
from django.test import TestCase, RequestFactory

from tests import faker
from tests.user.utils import create_user

from .utils import create_token

class AuthorizationMiddlewareTestCase(TestCase):
	def setUp(self):
		self.user = create_user()
		self.token = create_token(user_id = self.user.id)
		self.request_factory = RequestFactory()
		self.HEADER_PREFIX = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['JWT_AUTH_HEADER_PREFIX']


class HTTPAuthorizationTestCase(TestCase):
	def setUp(self):
		self.user = create_user()


class GetHTTPAuthorizationTestCase(TestCase):
	def setUp(self):
		self.user = create_user()
		self.request_factory = RequestFactory()
		self.HEADER_PREFIX = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['JWT_AUTH_HEADER_PREFIX']
