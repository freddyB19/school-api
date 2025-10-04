from unittest import mock

from graphql import GraphQLError

from apps.graphql.utils import (
	get_user,
	get_payload,
	decode_token,
	get_user_by_id,
	get_user_by_payload,
	get_http_authorization,
)
from apps.graphql import exceptions

from .utils import encode_token, PAYLOAD_SET_EXP
from .utils import testcases


class GetHTTPAuthorizationTest(testcases.GetHTTPAuthorizationTestCase):		

	def test_get_authorization_header(self):
		"""
			Obtener token del 'header'
		"""
		headers = {
			self.HEADER_NAME: f"{self.HEADER_PREFIX} {self.token}"
		}

		request = self.request_factory.get("/", **headers)

		auth_header = get_http_authorization(request = request)

		self.assertEqual(auth_header, self.token)


	def test_invalid_header_prefix(self):
		"""
			Obtener un 'None' por pasar un prefijo incorrecto en el 'header'
		"""
		headers = {
			self.HEADER_NAME: f"Token {self.token}"
		}

		request = self.request_factory.get("/", **headers)
		
		auth_header = get_http_authorization(request = request)

		self.assertIsNone(auth_header)

	def test_without_authorization_header(self):
		"""
			Obtener un 'None' por no pasar nada en el 'header'
		"""
		headers = {}
		
		request = self.request_factory.get("/", **headers)
		
		auth_header = get_http_authorization(request = request)

		self.assertIsNone(auth_header)


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


class GetUserByIDTest(testcases.HTTPAuthorizationTestCase):

	def test_get_user(self):
		"""
			Obtener un usuario por su ID
		"""
		user_id = self.user.id

		user = get_user_by_id(user_id)

		self.assertIsNotNone(user)
		self.assertEqual(user.id, user_id)


	def test_user_does_not_exists(self):
		"""
			Obtener un 'None' cuando no existe un usuario
		"""
		user_id = 5

		user = get_user_by_id(user_id)

		self.assertIsNone(user)


class GetUserbyPayloadTest(testcases.HTTPAuthorizationTestCase):

	def test_get_user_by_payload(self):
		"""
			Obtener un usuario mediate un diccionario que almecena el ID de un usuario
		"""

		payload = {"user_id": self.user.id}

		user = get_user_by_payload(payload)

		self.assertTrue(user)
		self.assertEqual(user.id, self.user.id)


	def test_get_user_by_invalid_payload(self):
		"""
			Enviando un diccionario con formato invalido
		"""

		with self.assertRaises(exceptions.InvalidPayload):
			user = get_user_by_payload({})


	def test_get_user_does_not_exists_by_payload(self):
		"""
			Intentar obtener un usuario que no existe
		"""
		payload = {"user_id": 5}
		
		with self.assertRaises(exceptions.InvalidUser):
			user = get_user_by_payload(payload)

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

		with self.assertRaises(exceptions.UserIsNotActive):
			user = get_user_by_payload(payload)


class GetPayloadTest(testcases.HTTPAuthorizationTestCase):

	def test_get_payload_from_token(self):
		"""
			Obtener información apartir de un token
		"""
		token = encode_token(user = self.user)

		payload = get_payload(token)

		self.assertTrue(isinstance(payload, dict))

	def test_error_from_invalid_token(self):
		token = encode_token(user = self.user, exp_time=PAYLOAD_SET_EXP({"seconds": -1}))

		with self.assertRaises(GraphQLError):
			payload = get_payload(token)


class GetUserTest(testcases.HTTPAuthorizationTestCase):

	def test_get_user_from_payload(self):
		"""
			Obtener un usuario a partir de un 'payload'
		"""

		payload = {"user_id": self.user.id}

		user = get_user(payload)

		self.assertIsNotNone(user)
		self.assertEqual(user.id, self.user.id)

	def test_get_user_from_invalid_payload(self):
		"""
			Intentando obtener un usuario de un 'payload' incorrecto
		"""

		user = get_user({})

		self.assertIsNone(user)

	@mock.patch(
		"apps.graphql.utils.UserModel.is_active",
		new_callable = mock.PropertyMock,
		return_value =  False
	)
	def test_get_disabled_user_from_payload(self, *args):
		"""
			Intentando obtener un usuario desactivado 
		"""
		payload = {"user_id": self.user.id}

		user = get_user(payload)

		self.assertIsNone(user)

	def test_get_user_does_not_exists_from_payload(self):
		"""
			Intentando obtener un usuario que no existe
		"""

		payload = {"user_id": 5}

		user = get_user(payload)

		self.assertIsNone(user)