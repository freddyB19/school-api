from typing import Optional
from pydantic import BaseModel, Field
from apps.utils.result_commands import MessageError
from apps.utils.decorators import handler_validation_errors

class User(BaseModel):
	name: str = Field(max_length = 30, min_length = 5)
	age: int = Field(gt = 18)


@handler_validation_errors
def set_user(user: User, errors: Optional[list[MessageError]] = None) -> dict:
	if errors:
		return {"status": "error", "details": errors}

	return {"status": "success", "details": user.model_dump()}