from rest_framework.test import APIClient, APITestCase

from . import utils


class SchoolTestCase(APITestCase):
	def setUp(self):
		self.client = APIClient()
		self.school = utils.create_school()


class SettingsFormatTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		self.school.setting.colors.set((utils.create_color_hex_format(), ))
		self.settings_format = self.school.setting


class OfficeHourTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		office_hours = utils.bulk_create_officehour(
			size = 5, 
			school = self.school
		)

		self.office_hour = office_hours[0]


class CalendarTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		calendars = utils.bulk_create_calendar(
			size = 10, 
			school = self.school
		)
		self.calendar = calendars[0]


class SocialMediaTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		utils.bulk_create_social_media(
			size = 4, 
			school = self.school
		)


class CoordinateTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		utils.bulk_create_coordinate(
			size = 10, 
			school = self.school
		)


class GradeTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		grades = utils.bulk_create_grade(
			size = 10, 
			school = self.school
		)
		self.grade = grades[0]


class RepositoryTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		repositories = utils.bulk_create_repository(
			size = 15, 
			school = self.school
		)
		self.repository = repositories[0]


class InfraestructureTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		list_infra = utils.bulk_create_infraestructure(
			size = 5, 
			school = self.school
		)
		self.infra = list_infra[0]


class DownloadsTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		downloads = utils.bulk_create_download(
			size = 10, 
			school = self.school
		)
		self.download = downloads[0]


class NewsTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		list_news = utils.bulk_create_news(
			size = 15, 
			school = self.school
		)
		self.news = list_news[0]


class CulturalEventsTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		cultual_events = utils.bulk_create_cultura_event(
			size = 10, 
			school = self.school
		)
		self.cultual_event = cultual_events[0]


class PaymentInfoTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		list_payment_info = utils.bulk_create_payment_info(
			size = 3, 
			school = self.school
		)
		self.payment_info = list_payment_info[0]


class ContacInfoTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		utils.bulk_create_contac_info(size = 3, school = self.school)


class ExtraActivityTestCase(SchoolTestCase):
	def setUp(self):
		super().setUp()
		extra_activities = utils.bulk_create_extra_activity(
			size = 6,
			school = self.school
		)
		self.extra_activity = extra_activities[0]