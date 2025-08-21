class JWTError(Exception):
	default_message = "Error en el JWT"

	def __init__(self, message:str = None) -> None:
		if not message:
			message = self.default_message

		super().__init__(message)


class JWTDecodeError(JWTError):
	default_message = "Error al extraer los datos del token"


class InvalidPayload(JWTError):
	default_message = "Los datos obtenidos del token no son correctos, es un 'payload' incorrecto"

class InvalidUser(JWTError):
	default_message = "No existe información sobre este usuario"


class UserIsNotActive(JWTError):
	default_message = "El usuario posee una cuenta desactivada"

class IsAuthenticated(JWTError):
	default_message = "El usuario no está autenticado"


JWT_ERROR_MESSAGE_EXPIRED = "El token a expirado"
JWT_ERROR_MESSAGE_INVALID = "Firma del token no valida"
JWT_ERROR_MESSAGE_IMMATURE = "Error en la estimación del tiempo del token"
JWT_ERROR_MESSAGE_DECODE = "No hay suficientes segmentos en el token"
