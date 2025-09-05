from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, model_validator, ConfigDict, Field, ValidationInfo

class BaseMessage(BaseModel):
	message: str = "Algo ha ocurrido"

class MessageError(BaseMessage):
	field: str
	details: dict[str, str] | None = None


WITHOUT_ERRORS = "Al definir 'error_code', también debe definir 'errors'"
WITHOUT_ERROR_CODE = "Al definir 'errors', también debe definir 'error_code'"
WITHOUT_ERROR_CODE_AND_ERRORS = "Al definir 'status', también debe definir 'errors' y 'error_code'"

HAS_WITHOUT_ERRORS_AND_ERROR_CODE = lambda errors, error_code: errors is None and error_code is None
HAS_ERRORS_WITHOUT_ERROR_CODE = lambda errors, error_code: errors is not None and error_code is None
HAS_ERROR_CODE_WITHOUT_ERRORS = lambda errors, error_code: error_code is not None and errors is None

# Limites para el código de error
GREATER_EQUAL = 400
LESS_THAN = 600 

# Buscar como trabajar con genericos
class ResultCommand(BaseModel):
	model_config = ConfigDict(frozen = True, extra='forbid')

	status: bool = True
	query: list[Any] | Any | None = None
	errors: list[BaseMessage]  | list[MessageError] | None = None
	error_code: int | None = Field(default = None, ge = GREATER_EQUAL, lt = LESS_THAN)

	@model_validator(mode = "after")
	def check_validation(self) -> Self:
		if not self.status:

			if HAS_WITHOUT_ERRORS_AND_ERROR_CODE(errors = self.errors, error_code = self.error_code):
				raise ValueError(WITHOUT_ERROR_CODE_AND_ERRORS)
			
			if HAS_ERRORS_WITHOUT_ERROR_CODE(errors = self.errors, error_code = self.error_code):
				raise ValueError(WITHOUT_ERROR_CODE)

			if HAS_ERROR_CODE_WITHOUT_ERRORS(errors = self.errors, error_code = self.error_code):
				raise ValueError(WITHOUT_ERRORS)

		return self


class ResponseMessage(BaseModel):
	message: str = "A message"
	

class ResponseSuccess(BaseModel):
	success: list[ResponseMessage] | list[BaseMessage]

class ResponseError(BaseModel):
	errors: list[ResponseMessage] | list[BaseMessage]

