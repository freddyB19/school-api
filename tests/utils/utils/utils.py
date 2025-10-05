from typing import Optional
from pydantic import BaseModel, Field
from apps.utils.result_commands import MessageError
from apps.utils.decorators import handler_validation_errors

MIN_LEN_NAME = 5
MAX_LEN_NAME = 30
AGE_GT = 18

class User(BaseModel):
	name: str = Field(max_length = MAX_LEN_NAME, min_length = MIN_LEN_NAME)
	age: int = Field(gt = AGE_GT)


@handler_validation_errors
def set_user(user: User, errors: Optional[list[MessageError]] = None) -> dict:
	if errors:
		return {"status": "error", "details": errors}

	return {"status": "success", "details": user.model_dump()}