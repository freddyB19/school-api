
from pydantic import BaseModel

class CreateUserParam(BaseModel):
	name: str
	email: str
	password: str