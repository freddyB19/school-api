from django.test import Client

from graphene_django.utils.testing import GraphQLTestCase

from tests.school.utils import create_school
from tests.user.utils import bulk_create_user, create_user

from apps.management.models import Administrator

from . import schemas, utils


class AdminDetailQueryTestCase(GraphQLTestCase):

	def setUp(self):
		self.client = Client()

		self.school = create_school()
		self.users = bulk_create_user(size = 6)
		
		token = utils.authorization_user()
		self.headers = {
			"Authorization": f"Bearer {token}"
		}

		self.administrator = Administrator.objects.get(school_id = self.school.id)
		self.administrator.users.set(self.users)

		self.query_administrator_detail = schemas.QUERY_ADMINISTRATOR_DETAIL		
		self.variables_administrator_detail = {
			"pk": self.administrator.id,
		}