from django.test import TransactionTestCase

from rest_framework.test import APIClient, APITestCase

from apps.management.tests import faker
from apps.user.tests.utils.utils import (
	create_user, 
	create_permissions, 
	get_permissions
)
from apps.school.tests.utils.utils import create_school, create_daysweek

from .utils import get_long_string, get_administrator


class CommandNewsTest(TransactionTestCase):
	def setUp(self):
		self.school = create_school()


class CommandTimeGroupTest(TransactionTestCase):
	def setUp(self):
		self.dayweek = create_daysweek()


class CommandOfficeHourTest(TransactionTestCase):
	def setUp(self):
		self.school = create_school()


class AdministratorTest(APITestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1)
		self.administrator = get_administrator(school_id = self.school.id)
		self.administrator.users.add(*[self.user_role_admin, self.user_role_staff])


class AdministratorUserTest(APITestCase):
	def setUp(self):
		self.client = APIClient()
		
		create_permissions()

		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1)

		create_permissions("Create test", "create_test")
		create_permissions("Read test", "read_test")
		create_permissions("Delete test", "delete_test")
		create_permissions("Update test", "update_test")


class SchoolUpdateTest(TransactionTestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_with_perm = create_user(role = 0)
		self.user_without_perm = create_user(role = 0, email = faker.email())

		self.permissions = get_permissions(codenames = ["change_school"])

		self.user_with_perm.user_permissions.set(self.permissions)
		
		admin = get_administrator(school_id = self.school.id)		
		admin.users.add(*(self.user_with_perm, self.user_without_perm))


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

		admin = get_administrator(school_id = self.school.id)

		admin.users.add(self.user_with_all_perm)


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

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(*(self.user_with_view_perm, self.user_with_delete_perm))


class NewsDetailUpdateDeleteTest(NewsCreateTest):
	def setUp(self):
		super().setUp()

		self.user_with_update_perm = create_user(role = 0, email = faker.email())

		self.user_with_update_perm.user_permissions.set(
			get_permissions(codenames = ["change_news"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_update_perm)


class NewsListTest(NewsTest):
	def setUp(self):
		super().setUp()


class OfficeHourTest(APITestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.dayweek = create_daysweek()
		self.user_with_all_perm = create_user(role = 0)

		permissions = get_permissions(codenames = [
			'add_officehour', 
			'change_officehour', 
			'delete_officehour', 
			'view_officehour'
		])

		self.user_with_all_perm.user_permissions.set(permissions)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_all_perm)


class OfficeHourCreateTest(OfficeHourTest):
	def setUp(self):
		super().setUp()

		self.user_with_view_perm = create_user(role = 0)
		self.user_with_delete_perm = create_user(role = 0)
		self.user_with_add_perm = create_user(role = 0)

		self.user_with_add_perm.user_permissions.set(
			get_permissions(codenames = ["add_officehour"])
		)
		self.user_with_view_perm.user_permissions.set(
			get_permissions(codenames = ["view_officehour"])
		)
		self.user_with_delete_perm.user_permissions.set(
			get_permissions(codenames = ["delete_officehour"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(*(
			self.user_with_add_perm,
			self.user_with_view_perm, 
			self.user_with_delete_perm,
		))


class OfficeHourListTest(OfficeHourCreateTest):
	def setUp(self):
		super().setUp()

		self.user_with_change_perm = create_user(role = 0)

		self.user_with_change_perm.user_permissions.set(
			get_permissions(codenames = ["change_officehour"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_change_perm)



class OfficeHourDetailUpdateDeleteTest(OfficeHourCreateTest):
	def setUp(self):
		super().setUp()
		
		self.user_with_change_perm = create_user(role = 0)

		self.user_with_change_perm.user_permissions.set(
			get_permissions(codenames = ["change_officehour"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_change_perm)