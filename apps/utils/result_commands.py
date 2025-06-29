from typing import Any
from pydantic import BaseModel

class BaseMessage(BaseModel):
	message: str = "Algo ha ocurrido"

class MessageError(BaseMessage):
	field: str
	details: dict[str, str] | None = None


# Buscar como trabajar con genericos
class ResultCommand(BaseModel):
	status: bool = True
	query: list[Any] | Any | None = None
	errors: list[BaseMessage]  | list[MessageError] | None = None


class ResponseMessage(BaseModel):
	message: str = "A message"
	

class ResponseSuccess(BaseModel):
	success: list[ResponseMessage]

class ResponseError(BaseModel):
	errors: list[ResponseMessage]

