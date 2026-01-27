from tests import faker

from apps.user import models

from tests.user.utils import create_user
from tests.graphql.utils import get_token

def authorization_user() -> dict[str, str | models.User]:
	EMAIL = faker.email()
	PASSWORD = faker.password()
	
	user = create_user(email = EMAIL, password = PASSWORD)
	return {
		"token": get_token(email = EMAIL, password = PASSWORD),
		"user": user
	}