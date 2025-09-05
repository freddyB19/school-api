from django.test import TransactionTestCase

from rest_framework.test import APIClient, APITestCase

from faker import Faker

from apps.user.tests.utils.utils import (
	create_user, 
	create_permissions, 
	get_permissions
)
from apps.school.tests.utils.utils import create_school

from .utils import get_long_string

faker = Faker(locale = "es")


UPDATE_SCHOOL_WITH_WRONG_DATA = [
	{
		"update": {
			"name": "Av12"
		},
		"expect": {
			"code": 400,
			"field": "name",
		}
	},
	{
		"update": {
			"name": get_long_string()
		},
		"expect": {
			"code": 400,
			"field": "name",
		}
	},
	{
		"update": {
			"address": get_long_string()
		},
		"expect": {
			"code": 400,
			"field": "address",
		}
	},
	{
		"update": {
			"address": "short"
		},
		"expect": {
			"code": 400,
			"field": "address",
		}
	},
	{
		"update": {
			"mission": "short"
		},
		"expect": {
			"code": 400,
			"field": "mission",
		}
	},
	{
		"update": {
			"vision": "short"
		},
		"expect": {
			"code": 400,
			"field": "vision",
		}
	},
	{
		"update": {
			"history": "short"
		},
		"expect": {
			"code": 400,
			"field": "history",
		}
	},
]


class SchoolUpdateTest(TransactionTestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_with_perm = create_user(role = 0)
		self.user_without_perm = create_user(role = 0, email = faker.email())

		self.permissions = get_permissions(codenames = ["change_school"])

		self.user_with_perm.user_permissions.set(self.permissions)


class NewsTest(APITestCase):
	def setUp(self):
		self.client = APIClient()
		self.school = create_school()
		self.user_with_all_perm = create_user(role = 0, email = faker.email())
		
		self.permissions = get_permissions(codenames = [
			"add_news",
			"change_news",
			"delete_news",
			"view_news",
		])

		self.user_with_all_perm.user_permissions.set(self.permissions)


class NewsCreateTest(NewsTest):
	def setUp(self):
		super().setUp()

		self.user_with_view_perm = create_user(role = 0, email = faker.email())
		self.user_with_delete_perm = create_user(role = 0, email = faker.email())

		self.user_with_view_perm.user_permissions.set(
			get_permissions(codenames = ["view_news"])
		)
		self.user_with_delete_perm.user_permissions.set(
			get_permissions(codenames = ["delete_news"])
		)




class CommandNewsTest(TransactionTestCase):
	def setUp(self):
		self.school = create_school()
		