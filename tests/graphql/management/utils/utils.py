from tests import faker

from tests.user.utils import create_user
from tests.graphql.utils import get_token

def authorization_user() -> str:
	EMAIL = faker.email()
	PASSWORD = faker.password()

	user = create_user(email = EMAIL, password = PASSWORD)
	return get_token(email = EMAIL, password = PASSWORD)