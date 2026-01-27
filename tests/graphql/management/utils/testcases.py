
from django.test import TestCase

from strawberry_django.test.client import TestClient

from apps.management import models

from tests.school.utils import create_school
from tests.user.utils import bulk_create_user, create_user

from . import schemas, utils

URL = "/graphql"

class AdminDetailQueryTestCase(TestCase):

	def setUp(self):
		self.client = TestClient(URL)

		self.school = create_school()
		
		self.authorization = utils.authorization_user()
		self.headers = {
			"Authorization": f"Bearer {self.authorization['token']}"
		}

		self.administrator = models.Administrator.objects.prefetch_related(
			"users"
		).get(school_id = self.school.id)
		
		self.administrator.users.add(self.authorization['user'])
		self.administrator.users.add(*bulk_create_user(size = 6))

		self.query = schemas.QUERY_ADMINISTRATOR_DETAIL		
		self.variables = {
			"pk": self.administrator.id
		}
