from unittest import mock

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from freezegun import freeze_time

from tests import faker

from apps.graphql.utils import (
	decode_token,
	get_user_by_payload,
	get_user_from_token,
	get_http_authorization,
)
from apps.graphql import exceptions

from .utils import testcases, encode_token, PAYLOAD_SET_EXP, create_token


class GetHTTPAuthorizationTest(testcases.GetHTTPAuthorizationTestCase):
	def setUp(self):
		super().setUp()
		self.token = faker.sha256()	

	def test_get_authorization_header(self):
		"""
			Obtener token del 'Header'
		"""
		headers = f"{self.HEADER_PREFIX} {self.token}"

		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

		is_token = get_http_authorization(request = request)

		self.assertTrue(is_token)
		self.assertIsInstance(is_token, str)

	def test_invalid_header_prefix(self):
		"""
			Obtener un 'None' por pasar un prefijo incorrecto en el 'Header'
		"""
		headers = f"Token {self.token}"

		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)
		
		is_token = get_http_authorization(request = request)

		self.assertIsNone(is_token)

	def test_without_authorization_header(self):
		"""
			Obtener un 'None' por no pasar nada en el 'Header'
		"""
		headers = {}
		
		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)
		
		is_token = get_http_authorization(request = request)

		self.assertIsNone(is_token)


class DecodeTokenTest(testcases.HTTPAuthorizationTestCase):

	def test_expired_token(self):
		"""
			El token recibido ha expirado
		"""
		token = encode_token(self.user, exp_time = PAYLOAD_SET_EXP({"seconds": -1}))

		with self.assertRaisesMessage(exceptions.JWTDecodeError, exceptions.JWT_ERROR_MESSAGE_EXPIRED):
			decode_token(token)

	def test_decode_error(self):
		"""
			Ausencia de segmentos en el token
		"""
		token = encode_token(self.user, exp_time = PAYLOAD_SET_EXP())

		with self.assertRaisesMessage(exceptions.JWTDecodeError, exceptions.JWT_ERROR_MESSAGE_DECODE):
			decode_token(token[1:])


class GetUserbyPayloadTest(testcases.HTTPAuthorizationTestCase):

	def test_get_user_by_payload(self):
		"""
			Obtener un usuario mediate un diccionario que almecena el ID de un usuario
		"""
		payload = {"user_id": self.user.id}

		user = get_user_by_payload(payload)

		self.assertNotIsInstance(user, AnonymousUser)
		self.assertEqual(user.id, self.user.id)

	def test_get_user_by_invalid_payload(self):
		"""
			Enviando un diccionario con formato invalido
		"""
		user = get_user_by_payload({})

		self.assertIsInstance(user, AnonymousUser)

	def test_get_user_does_not_exists_by_payload(self):
		"""
			Intentar obtener un usuario que no existe
		"""
		payload = {"user_id": 5}
		
		user = get_user_by_payload(payload)
		self.assertIsInstance(user, AnonymousUser)


	@mock.patch(
		"apps.graphql.utils.UserModel.is_active",
        new_callable=mock.PropertyMock,
		return_value = False
	)
	def test_user_disabled_by_payload(self, *args):
		"""
			Intentar obtener un usuario que esta desactivado
		"""
		payload = {"user_id": self.user.id}

		user = get_user_by_payload(payload)
		self.assertIsInstance(user, AnonymousUser)


class GetUserFromToken(testcases.GetHTTPAuthorizationTestCase):

	def test_valid_token(self):
		"""
			Validar obtener un usuario desde un token
		"""
		token = create_token(user_id = self.user.id)
		headers = f"{self.HEADER_PREFIX} {token}"
		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

		is_user = get_user_from_token(request = request)

		self.assertNotIsInstance(is_user, AnonymousUser)
		self.assertEqual(is_user.id, self.user.id)

	def test_valid_token_with_invalid_header(self):
		"""
			Obtener un usuario 'Anonimo' por  petición con una cabecera invalida
		"""
		token = create_token(user_id = self.user.id)
		headers = f"JWT {token}"
		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

		is_user = get_user_from_token(request = request)
		self.assertIsInstance(is_user, AnonymousUser)

	def test_valid_expired_token(self):
		"""
			Obtener un usuario 'Anonimo' por token expirado
		"""
		curre_date = timezone.localtime()

		create_date = f"{curre_date.year}-{curre_date.month}-{curre_date.day}"

		with freeze_time(f"{create_date} 12:00"):
			expired_token = encode_token(user = self.user)
		
		headers = f"{self.HEADER_PREFIX} {expired_token}"
		
		with freeze_time(f"{create_date} 15:00"):
			request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

			is_user = get_user_from_token(request = request)

			self.assertIsInstance(is_user, AnonymousUser)

	@mock.patch(
		"apps.graphql.utils.UserModel.is_active",
        new_callable=mock.PropertyMock,
		return_value = False
	)
	def test_valid_token_with_disabled_user(self, *args):
		"""
			Obtener un usuario 'Anonimo' por cuenta del usuario desactivada
		"""
		token = create_token(user_id = self.user.id)
		headers = f"{self.HEADER_PREFIX} {token}"
		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

		is_user = get_user_from_token(request = request)
		self.assertIsInstance(is_user, AnonymousUser)

	def test_valid_token_with_non_existent_user(self):
		"""
			Obtener un usuario 'Anonimo' por cuenta del usuario no existente
		"""
		wrong_user_id = get_user_model().objects.last().id
		
		token = create_token(user_id = faker.random_int(min = wrong_user_id + 1))
		headers = f"{self.HEADER_PREFIX} {token}"
		request = self.request_factory.get("/", HTTP_AUTHORIZATION = headers)

		is_user = get_user_from_token(request = request)
		self.assertIsInstance(is_user, AnonymousUser)
