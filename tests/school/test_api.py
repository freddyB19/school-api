import unittest, datetime

from django.urls import reverse
from django.utils import timezone


from apps.school import models

from tests import faker

from .utils import utils, testcases


class SchoolAPITest(testcases.SchoolTestCase):
	def setUp(self):
		super().setUp()
		self.URL_SCHOOL = self.get_school_url(subdomain =  self.school.subdomain)
		self.URL_SCHOOL_DETAIL = self.get_detail_school_url(id = self.school.id)

	def get_school_url(self, subdomain):
		return reverse(
			"school:school", 
			query={"subdomain": subdomain}
		)

	def get_detail_school_url(self, id):
		return reverse("school:detail", kwargs={"pk": id})

	def test_get_school(self):
		"""
			Validar "GET /school"
		"""
		response = self.client.get(self.URL_SCHOOL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertEqual(responseJson["name"], self.school.name)
		self.assertEqual(responseJson["subdomain"], self.school.subdomain)
		self.assertEqual(responseJson["logo"], self.school.logo)
		self.assertEqual(responseJson["address"], self.school.address)
		self.assertEqual(responseJson["mission"], self.school.mission)
		self.assertEqual(responseJson["private"], self.school.private)


	def test_get_school_detail(self):
		"""
			Validar "GET /school/:id"
		"""

		response = self.client.get(self.URL_SCHOOL_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.school.id)
		self.assertEqual(responseJson["name"], self.school.name)
		self.assertEqual(responseJson["subdomain"], self.school.subdomain)
		self.assertEqual(responseJson["logo"], self.school.logo)
		self.assertEqual(responseJson["address"], self.school.address)
		self.assertEqual(responseJson["mission"], self.school.mission)
		self.assertEqual(responseJson["vision"], self.school.vision)
		self.assertEqual(responseJson["history"], self.school.history)
		self.assertEqual(responseJson["private"], self.school.private)


	def test_get_school_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /school/:id" por información que no existe
		"""
		school_id = models.School.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = school_id + 1)

		response = self.client.get(
			self.get_detail_school_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class SettingsFormatAPITest(testcases.SettingsFormatTestCase):

	def setUp(self):
		super().setUp()

		self.URL_SETTINGS_FORMAT = self.get_school_settingsformat_url(
			school_id = self.school.id
		)

	def get_school_settingsformat_url(self, school_id):
		return reverse("school:settings", kwargs={"pk": school_id})


	def test_get_settings_format(self):
		"""
			Validar "GET/school/:id/settings"
		"""
		colors = [color.color for color in self.settings_format.colors.all()]

		response = self.client.get(self.URL_SETTINGS_FORMAT)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson['colors'], colors)


class OfficeHourAPITest(testcases.OfficeHourTestCase):
	def setUp(self):
		super().setUp()
		self.URL_OFFICE_HOUR = self.get_school_officehour_url(school_id = self.school.id)
		self.URL_OFFICE_HOUR_DETAL = self.get_detail_officehour_url(id = self.office_hour.id)

	def get_school_officehour_url(self, school_id):
		return reverse("school:office-hour", kwargs = {"pk": school_id})

	def get_detail_officehour_url(self, id):
		return reverse("school:office-hour-detail", kwargs = {"pk": id})


	def test_get_office_hour(self):
		"""
			Validar "GET /school/:id/officehour"
		"""
		total_officehour = models.OfficeHour.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_OFFICE_HOUR)

		responseJson = response.data
		responseStatus = response.status_code


		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_officehour)

		

	def test_get_office_hour_detail(self):
		"""
			Validar "GET /officehour/:id"
		"""
		response = self.client.get(self.URL_OFFICE_HOUR_DETAL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.office_hour.id)
		self.assertEqual(responseJson["interval_description"], self.office_hour.interval_description)
		self.assertEqual(responseJson["time_group"]["id"], self.office_hour.time_group.id)
		self.assertEqual(responseJson["time_group"]["type"], self.office_hour.time_group.type)

	def test_get_office_hour_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /officehour/:id" por información que no existe
		"""
		office_hour_id = models.OfficeHour.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = office_hour_id + 1)

		response = self.client.get(
			self.get_detail_officehour_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class CalendarAPITests(testcases.CalendarTestCase):
	def setUp(self):
		super().setUp()
		self.URL_CALENDAR = self.get_school_calendar_url(school_id = self.school.id)
		self.URL_CALENDAR_DETAIL = self.get_detail_calendar_url(id = self.calendar.id)

	def get_school_calendar_url(self, school_id, **extra):
		return reverse("school:calendar", 
			kwargs={"pk": school_id},
			**extra
		)

	def get_detail_calendar_url(self, id):
		return reverse("school:calendar-detail", kwargs={"pk": id})

	def delete_all_from_db(self):
		models.Calendar.objects.all().delete()

	def test_get_calendar(self):
		"""
			Validar "GET /school/:id/calendar"
		"""
		# Creamos fechas para el mes actual
		utils.bulk_create_calendar(
			size = 4, 
			school = self.school,
			date = faker.date_this_month()
		)

		total_calendar = models.Calendar.objects.filter(
			school_id = self.school.id
		).count()
		
		total_calendar_actual_month = models.Calendar.objects.filter(
			school_id = self.school.id,
			date__month = timezone.now().month
		).count()

		response = self.client.get(self.URL_CALENDAR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertNotEqual(responseJson["count"], total_calendar)
		self.assertEqual(responseJson["count"], total_calendar_actual_month)

	def test_get_calendar_by_filter(self):
		"""
			Validar "GET /school/:id/calendar?month=<...>"
		"""
		self.delete_all_from_db()

		date = timezone.now()

		JAN = 1
		NOV = 11

		date_jan = datetime.date(date.year, JAN, date.day)
		date_nov = datetime.date(date.year, NOV, date.day)
		total_calendar_jan = 3
		total_calendar_nov = 6

		utils.bulk_create_calendar(
			size = total_calendar_jan, 
			school = self.school,
			date = date_jan
		)
		utils.bulk_create_calendar(
			size = total_calendar_nov, 
			school = self.school,
			date = date_nov
		)

		test_case = [
			{"month": JAN, "total_calendar": total_calendar_jan},
			{"month": NOV, "total_calendar": total_calendar_nov}
		]

		for case in test_case:
			with self.subTest(case = case):	
				response = self.client.get(self.get_school_calendar_url(
					school_id = self.school.id,
					query={"month": case["month"]}
				))

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 200)

				self.assertEqual(responseJson["count"], case["total_calendar"])


	def test_get_calendar_detail(self):
		"""
			Validar "GET /calendar/:id"
		"""
		response = self.client.get(self.URL_CALENDAR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.calendar.id)
		self.assertEqual(responseJson["title"], self.calendar.title)
		self.assertEqual(responseJson["description"], self.calendar.description)


	def test_get_calendar_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /calendar/:id" por información que no existe
		"""
		calendar_id = models.Calendar.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = calendar_id + 1)

		response = self.client.get(
			self.get_detail_calendar_url(id = wrong_pk)
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 404)


class SocialMediaAPITest(testcases.SocialMediaTestCase):
	def setUp(self):
		super().setUp()
		self.URL_SOCIAL_MEDIA = self.get_school_social_media_url(school_id = self.school.id)

	def get_school_social_media_url(self, school_id):
		return reverse("school:social-media", kwargs={"pk": school_id})

	def test_get_social_media(self):
		"""
			Validar "GET /school/:id/socialmedia"
		"""
		total_socialmedia = models.SocialMedia.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_SOCIAL_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_socialmedia)


class CoordinateAPITest(testcases.CoordinateTestCase):
	def setUp(self):
		super().setUp()
		self.URL_COORDINATE = self.get_school_coordinate_url(school_id = self.school.id)

	def get_school_coordinate_url(self, school_id):
		return reverse("school:coordinate", kwargs={"pk": school_id})

	def test_get_coordinate(self):
		"""
			Validar "GET /school/:id/coordinate"
		"""
		total_coordinate = models.Coordinate.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_COORDINATE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_coordinate)


class GradeAPITest(testcases.GradeTestCase):
	def setUp(self):
		super().setUp()
		self.URL_GRADE = self.get_school_grades_url(school_id = self.school.id)
		self.URL_GRADE_DETAIL = self.get_detail_grade_url(id = self.grade.id)

	def get_school_grades_url(self, school_id):
		return reverse("school:grade", kwargs={"pk": school_id})

	def get_detail_grade_url(self, id):
		return reverse("school:grade-detail", kwargs={"pk": id})

	def test_get_grade(self):
		"""
			Validar "GET /school/:id/grade"
		"""
		total_grades = models.Grade.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_GRADE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_grades)


	def test_get_grade_detail(self):
		"""
			Validar "GET /grade/:id"
		"""
		response = self.client.get(self.URL_GRADE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code
		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertEqual(responseJson["name"], self.grade.name)
		self.assertEqual(responseJson["description"], self.grade.description)
		self.assertEqual(responseJson["stage"], self.grade.stage.type)
		self.assertEqual(responseJson["section"], self.grade.section)


	def test_get_grade_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /grade/:id" por información que no existe
		"""
		grade_id = models.Grade.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = grade_id + 1)

		response = self.client.get(
			self.get_detail_grade_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class RepositoryAPITest(testcases.RepositoryTestCase):
	def setUp(self):
		super().setUp()
		self.URL_REPOSITORY = self.get_school_repositories_url(school_id = self.school.id)
		self.URL_REPOSITORY_DETAIL = self.get_detail_repository_url(id = self.repository.id)

	def get_school_repositories_url(self, school_id):
		return reverse("school:repository", kwargs={"pk": school_id})

	def get_detail_repository_url(self, id):
		return reverse("school:repository-detail", kwargs={"pk": id})

	def test_get_repository(self):
		"""
			Validar "GET /school/:id/repository"
		"""
		total_repositories = models.Repository.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_REPOSITORY)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_repositories)


	def test_get_repository_detail(self):
		"""
			Validar "GET /repository/:id"
		"""
		response = self.client.get(self.URL_REPOSITORY_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.repository.id)
		self.assertEqual(responseJson["name_project"], self.repository.name_project)
		self.assertEqual(responseJson["description"], self.repository.description)


	def test_get_repository_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /repository/:id" por información que no existe
		"""
		repository_id = models.Repository.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk =  faker.random_int(min = repository_id + 1)
		
		response = self.client.get(
			self.get_detail_repository_url(id  = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class InfraestructureAPITest(testcases.InfraestructureTestCase):
	def setUp(self):
		super().setUp()
		self.URL_INFRAESTRUCTURE = self.get_school_infra_url(school_id = self.school.id)
		self.URL_INFRAESTRUCTURE_DETAIL = self.get_detail_infra_url(id = self.infra.id)

	def get_school_infra_url(self, school_id):
		return reverse("school:infraestructure", kwargs={"pk": school_id})

	def get_detail_infra_url(self, id):
		return reverse("school:infraestructure-detail", kwargs={"pk": id})

	def test_get_infraestructure(self):
		"""
			Validar "GET /school/:id/infraestructure"
		"""
		total_infra = models.Infraestructure.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_INFRAESTRUCTURE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_infra)

	
	def test_get_infraestructure_detail(self):
		"""
			Validar "GET /infraestructure/:id"
		"""
		response = self.client.get(self.URL_INFRAESTRUCTURE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.infra.id)
		self.assertEqual(responseJson["name"], self.infra.name)
		self.assertEqual(responseJson["description"], self.infra.description)

	def test_get_infraestructure_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /infraestructure/:id" por información que no existe
		"""
		infra_id = models.Infraestructure.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = infra_id + 1)

		response = self.client.get(
			self.get_detail_infra_url(id = wrong_pk)
		)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 404)


class DownloadsAPITest(testcases.DownloadsTestCase):
	def setUp(self):
		super().setUp()
		self.URL_DOWNLOADS = self.get_school_downloads_url(school_id = self.school.id)
		self.URL_DOWNLOADS_DETAIL = self.get_detail_download_url(id = self.download.id)

	def get_school_downloads_url(self, school_id):
		return reverse("school:downloads", kwargs={"pk": school_id})

	def get_detail_download_url(self, id):
		return reverse("school:downloads-detail", kwargs={"pk":  id})

	def test_get_downloads(self):
		"""
			Validar "GET /school/:id/download"
		"""
		total_downloads = models.Download.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_DOWNLOADS)
		
		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_downloads)


	def test_get_downloads_detail(self):
		"""
			Validar "GET /download/:id"
		"""
		response = self.client.get(self.URL_DOWNLOADS_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.download.id)
		self.assertEqual(responseJson["title"], self.download.title)
		self.assertEqual(responseJson["file"], self.download.file)


	def test_get_downloads_detail_does_not_exists(self):
		"""
			Validar "GET /download/:id" por información que no existe
		"""
		download_id = models.Download.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = download_id + 1)

		response = self.client.get(
			self.get_detail_download_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class NewsAPITest(testcases.NewsTestCase):
	def setUp(self):
		super().setUp()
		self.URL_NEWS = self.get_school_news_url(school_id = self.school.id)
		self.URL_NEWS_DETAIL = self.get_detail_news_url(id =  self.news.id)

	def get_school_news_url(self, school_id):
		return reverse("school:news", kwargs={"pk": school_id})

	def get_detail_news_url(self, id):
		return reverse("school:news-detail", kwargs={"pk": id})

	def test_get_news(self):
		"""
			Validar "GET /school/:id/news"
		"""
		total_news = models.News.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_NEWS)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_news)


	def test_get_news_detail(self):
		"""
			Validar "GET /news/:id"
		"""
		response = self.client.get(self.URL_NEWS_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.news.id)
		self.assertEqual(responseJson["title"], self.news.title)
		self.assertEqual(responseJson["description"], self.news.description)


	def test_get_news_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /news/:id" que información que no existe
		"""
		news_id = models.News.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = news_id + 1)

		response = self.client.get(
			self.get_detail_news_url(id = wrong_pk)
		)

		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 404)


class CulturalEventsAPITest(testcases.CulturalEventsTestCase):
	def setUp(self):
		super().setUp()
		self.URL_CULTURAL_EVENTS = self.get_school_culturalevents_url(school_id = self.school.id)
		self.URL_CULTURAL_EVENTS_DETAIL = self.get_detail_culturalevent_url(id = self.cultual_event.id)

	def get_school_culturalevents_url(self, school_id):
		return reverse("school:cultural-events", kwargs={"pk": school_id})

	def get_detail_culturalevent_url(self, id):
		return reverse("school:cultural-events-detail", kwargs={"pk": id})

	def test_get_cultura_event(self):
		"""
			Validar "GET /school/:id/culturalevents"
		"""
		total_events = models.CulturalEvent.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_CULTURAL_EVENTS)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_events)


	def test_get_cultura_event_detail(self):
		"""
			Validar "GET /culturalevents/:id"
		"""
		response = self.client.get(self.URL_CULTURAL_EVENTS_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultual_event.id)
		self.assertEqual(responseJson["title"], self.cultual_event.title)
		self.assertEqual(responseJson["description"], self.cultual_event.description)


	def test_get_cultural_event_detail_does_not_exist(self):
		"""
			Generar [Error 404] "GET /culturalevents/:id" por información que no existe
		"""
		event_id = models.CulturalEvent.objects.last().id
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = event_id + 1)

		response = self.client.get(
			self.get_detail_culturalevent_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class PaymentInfoAPITest(testcases.PaymentInfoTestCase):
	def setUp(self):
		super().setUp()
		self.URL_PAYMENT_INFO = self.get_school_payments_info_url(
			school_id = self.school.id
		)
		self.URL_PAYMENT_INFO_DETAIL = self.get_detail_payment_info_url(
			id = self.payment_info.id
		)

	def get_school_payments_info_url(self, school_id):
		return reverse("school:payment-info", kwargs={"pk": school_id})
	
	def get_detail_payment_info_url(self, id):
		return reverse("school:payment-info-detail", kwargs={"pk": id})

	def test_get_payment_info(self):
		"""
			Validar "GET /school/:id/payment"
		"""
		total_payment_info  = models.PaymentInfo.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_PAYMENT_INFO)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_payment_info)


	def test_get_payment_info_detail(self):
		"""
			Validar "GET /payment/:id"
		"""
		response = self.client.get(self.URL_PAYMENT_INFO_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info.id)
		self.assertEqual(responseJson["title"], self.payment_info.title)
		self.assertEqual(responseJson["photo"], self.payment_info.photo)
		self.assertEqual(responseJson["description"], self.payment_info.description)

	def test_get_payment_info_with_school_does_not_exist(self):
		"""
			Generar [Error 404] "GET /payment/:id" por información que no existe
		"""
		payment_info_id = models.PaymentInfo.objects.last().id
		
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk = faker.random_int(min = payment_info_id + 1)
		
		response = self.client.get(
			self.get_detail_payment_info_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


class ContactInfoAPITest(testcases.ContacInfoTestCase):
	def setUp(self):
		super().setUp()
		self.URL_CONTACT_INFO = self.get_school_contactinfo_url(
			school_id = self.school.id
		)

	def get_school_contactinfo_url(self, school_id):
		return reverse("school:contact-info", kwargs={"pk": school_id})

	def test_get_contact_info(self):
		"""
			Validar "GET /school/:id/contact"
		"""
		total_contac_info = models.ContactInfo.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_CONTACT_INFO)
		
		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_contac_info)


class ExtraActivityAPITest(testcases.ExtraActivityTestCase):
	def setUp(self):
		super().setUp()
		self.URL_EXTRA_ACTIVITY = self.get_school_extra_activity_url(
			school_id = self.school.id
		)
		self.URL_EXTRA_ACTIVITY_DETAIL = self.get_detail_extra_activity_url(
			id = self.extra_activity.id
		)

	def get_school_extra_activity_url(self, school_id):
		return reverse("school:extra-activity", kwargs={"pk": school_id})

	def get_detail_extra_activity_url(self, id):
		return reverse("school:extra-activity-detail", kwargs={"pk": id})

	def test_get_extra_activity(self):
		"""
			Validar "GET /school/:id/activity"
		"""
		total_extra_activities = models.ExtraActivity.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_EXTRA_ACTIVITY)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["count"], total_extra_activities)


	def test_detail_extra_activity(self):
		"""
			Validar "GET /activity/:id"
		"""
		response = self.client.get(self.URL_EXTRA_ACTIVITY_DETAIL)
		
		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.extra_activity.id)
		self.assertEqual(responseJson["title"], self.extra_activity.title)
		self.assertEqual(responseJson["description"], self.extra_activity.description)


	def test_detail_extra_activity_does_not_exist(self):
		"""
			Generar [Error 404] "GET /activity/:id" por información que no existe
		"""
		extra_activity_id = models.ExtraActivity.objects.last().id

		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		wrong_pk =  faker.random_int(min = extra_activity_id + 1)

		response = self.client.get(
			self.get_detail_extra_activity_url(id = wrong_pk)
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
