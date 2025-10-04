from tests import faker

from graphene_django.utils.testing import GraphQLTestCase

from tests.user.utils import create_user
from tests.school.utils import create_school

from . import schemas

class AdminCreateUserTestCase(GraphQLTestCase):
	def setUp(self):
		 
		self.school = create_school()
		self.user = create_user()

		self.query_create_user = schemas.QUERY_CREATE_USER

		password = faker.password()
		self.variables_create_user = {
			"school_id": self.school.id,
			"user": {
				"name": faker.name(),
				"email": faker.email(), 
				"password": password, 
				"passwordConfirm": password
			}
		}