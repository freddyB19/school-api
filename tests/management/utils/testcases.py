from django.test import TransactionTestCase

from rest_framework.test import APIClient, APITestCase

from tests import faker

from tests.user.utils import (
	create_user, 
	create_permissions, 
	get_permissions
)
from tests.school.utils import (
	create_school, 
	create_daysweek, 
	create_time_group
)

from .utils import get_long_string, get_administrator

class AdministratorModelTestCase(TransactionTestCase):
	# serialized_rollback = True

	def setUp(self):
		self.school = create_school()


class CommandNewsTestCase(TransactionTestCase):
	def setUp(self):
		self.school = create_school()


class CommandTimeGroupTestCase(TransactionTestCase):
	def setUp(self):
		self.dayweek = create_daysweek()

class CommandGetOrCreateTimeGroupTestCase(TransactionTestCase):
	def setUp(self):
		self.time_group = create_time_group()
		

class CommandOfficeHourTestCase(TransactionTestCase):
	def setUp(self):
		self.school = create_school()


class AdministratorTestCase(APITestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1)
		self.administrator = get_administrator(school_id = self.school.id)
		self.administrator.users.add(*[self.user_role_admin, self.user_role_staff])


class AdministratorUserTestCase(APITestCase):
	def setUp(self):
		self.client = APIClient()
		
		create_permissions()

		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1)

		create_permissions("Create test", "create_test")
		create_permissions("Read test", "read_test")
		create_permissions("Delete test", "delete_test")
		create_permissions("Update test", "update_test")


class SchoolUpdateTestCase(TransactionTestCase):
	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_with_perm = create_user(role = 0)
		self.user_without_perm = create_user(role = 0, email = faker.email())

		self.permissions = get_permissions(codenames = ["change_school"])

		self.user_with_perm.user_permissions.set(self.permissions)
		
		admin = get_administrator(school_id = self.school.id)		
		admin.users.add(*(self.user_with_perm, self.user_without_perm))


class NewsTestCase(APITestCase):
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


class NewsCreateTestCase(NewsTestCase):
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


class NewsDetailUpdateDeleteTestCase(NewsCreateTestCase):
	def setUp(self):
		super().setUp()

		self.user_with_update_perm = create_user(role = 0, email = faker.email())

		self.user_with_update_perm.user_permissions.set(
			get_permissions(codenames = ["change_news"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_update_perm)


class NewsListTestCase(NewsTestCase):
	def setUp(self):
		super().setUp()


class OfficeHourTestCase(APITestCase):
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


class OfficeHourCreateTestCase(OfficeHourTestCase):
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


class OfficeHourListTestCase(OfficeHourCreateTestCase):
	def setUp(self):
		super().setUp()

		self.user_with_change_perm = create_user(role = 0)

		self.user_with_change_perm.user_permissions.set(
			get_permissions(codenames = ["change_officehour"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_change_perm)



class OfficeHourDetailUpdateDeleteTestCase(OfficeHourCreateTestCase):
	def setUp(self):
		super().setUp()
		
		self.user_with_change_perm = create_user(role = 0)

		self.user_with_change_perm.user_permissions.set(
			get_permissions(codenames = ["change_officehour"])
		)

		admin = get_administrator(school_id = self.school.id)
		admin.users.add(self.user_with_change_perm)