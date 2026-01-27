
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser


from freezegun import freeze_time

from apps.graphql.middleware import GraphqlJWTAuthMiddleware

from .utils import testcases, encode_token, PAYLOAD_SET_EXP, create_token


class JWTAuthorizationMiddlewareTest(testcases.AuthorizationMiddlewareTestCase):
	def setUp(self):
		super().setUp()
		self.URL = "/graphql"

	def test_authorization_user(self):
		"""
			Validar la autenticación de un usuario
		"""
		headers = f"{self.HEADER_PREFIX} {self.token}"

		request = self.request_factory.get(self.URL, HTTP_AUTHORIZATION = headers)

		middleware = GraphqlJWTAuthMiddleware(lambda get_request: get_request)
		middleware(request)

		self.assertTrue(request.user.is_authenticated)
		self.assertEqual(request.user.id, self.user.id)

	def test_authorization_user_with_invalid_prefix(self):
		"""
			No autenticar por enviar un prefijo invalido en el 'Header'
		"""
		headers = f"Token {self.token}"

		request = self.request_factory.get(self.URL, HTTP_AUTHORIZATION = headers)

		middleware = GraphqlJWTAuthMiddleware(lambda get_request: get_request)
		middleware(request)

		self.assertTrue(request.user.is_anonymous)

	def test_authorization_user_without_token(self):
		"""
			No autenticar por no enviar un token en el 'Header'
		"""
		headers = {}
		request_without_header = self.request_factory.get(self.URL)
		request_with_wrong_header = self.request_factory.get(
			self.URL, 
			HTTP_AUTHORIZATION = headers
		)

		middleware_without_header = GraphqlJWTAuthMiddleware(
			lambda get_request: get_request
		)
		middleware_without_header(request_without_header)

		middleware_with_wrong_header = GraphqlJWTAuthMiddleware(
			lambda get_request: get_request
		)
		middleware_with_wrong_header(request_with_wrong_header)

		self.assertTrue(request_without_header.user.is_anonymous)
		self.assertTrue(request_with_wrong_header.user.is_anonymous)

	def test_authorization_user_with_invalid_token(self):
		"""
			No autenticar por enviar un token invalido
		"""
		headers = f"{self.HEADER_PREFIX} esto-no-es-jwt"
		
		request = self.request_factory.get(self.URL, HTTP_AUTHORIZATION = headers)

		middleware = GraphqlJWTAuthMiddleware(lambda get_request: get_request)
		middleware(request)

		self.assertTrue(request.user.is_anonymous)

	def test_authorization_user_with_expired_token(self):
		"""
			No autenticar por enviar token expirado
		"""
		curre_date = timezone.localtime()

		create_date = f"{curre_date.year}-{curre_date.month}-{curre_date.day}"

		with freeze_time(f"{create_date} 12:00"):
			expired_token = encode_token(user = self.user, exp_time = PAYLOAD_SET_EXP())

		headers = f"{self.HEADER_PREFIX} {expired_token}"

		with freeze_time(f"{create_date} 15:00"):
		
			request = self.request_factory.get(self.URL, HTTP_AUTHORIZATION = headers)

			middleware = GraphqlJWTAuthMiddleware(lambda get_request: get_request)
			middleware(request)

			self.assertTrue(request.user.is_anonymous)


class MiddlewareEfficiencyTest(testcases.GetHTTPAuthorizationTestCase):
	def setUp(self):
		super().setUp()
		self.URL = "/graphql"
		token = create_token(user_id = self.user.id)
		self.headers = f"{self.HEADER_PREFIX} {token}"

	def test_middleware_is_lazy(self):
		"""
			Verificar que el middleware no consulta la DB hasta que alguien toca al usuario.
		"""
		request = self.request_factory.get(self.URL, HTTP_AUTHORIZATION = self.headers)
		middleware = GraphqlJWTAuthMiddleware(lambda get_request: get_request)
		
		with self.assertNumQueries(0):
			middleware(request)

		with self.assertNumQueries(1):
			self.assertTrue(request.user.is_authenticated)
