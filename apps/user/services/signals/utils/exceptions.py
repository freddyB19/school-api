
from apps.user import models

class SignalError(Exception):
	default_message = "Error en la señal enviada"

	def __init__(self, message: str = None) -> None:
		if not message:
			message = self.default_message

		super().__init__(message)


ERROR_MESSAGE_INVALID_PARAM_RESET_PASSWORD = "Debe pasar [plain_password, name, email]"

class InvalidParams(SignalError):
	default_message = ERROR_MESSAGE_INVALID_PARAM_RESET_PASSWORD


ERROR_MESSAGE_INVALID_ROLE = f"Debe ser un role valido {models.TypeRole.choices}"

class InvalidUserRole(SignalError):
	default_message = ERROR_MESSAGE_INVALID_ROLE


ERROR_MESSAGE_INVALID_VALUE = "Debe enviar un usuario"

class InvalidValue(SignalError):
	default_message = ERROR_MESSAGE_INVALID_VALUE