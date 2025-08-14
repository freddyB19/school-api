import unittest

from django.urls import reverse
from django.test import TransactionTestCase

from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from apps.school.apiv1 import views
from apps.school import models

from .utils import utils
class SchoolAPITest(TransactionTestCase):

	def setUp(self):
		self.client = APIClient()
		
		self.school = utils.create_school()
		self.school.setting.colors.set(utils.create_color_hex_format())
		
		self.settings_format = self.school.setting
		self.office_hour = utils.crea_office_hour(id = self.school.id)
		self.calendar = utils.create_calendar(id = self.school.id)
		self.social_media = utils.create_social_media(id = self.school.id)
		self.coordinate = utils.create_social_media(id = self.school.id)
		self.grade = utils.create_grade(id = self.school.id)
		self.repository = utils.create_repository(id = self.school.id)
		self.infra = utils.create_infraestructure(id = self.school.id)
		self.downloads = utils.create_download(id = self.school.id)
		self.news = utils.create_news(id = self.school.id)
		self.cultual_events = utils.create_cultura_event(id = self.school.id)
		self.payment_info = utils.create_payment_info(id = self.school.id)
		self.contact_info = utils.create_contac_info(id = self.school.id)
		self.extra_activitie = utils.create_extra_activitie(id = self.school.id)



		self.URL_SCHOOL = reverse("school:school", query={"subdomain": self.school.subdomain}) 
		self.URL_SCHOOL_DETAIL = reverse("school:detail", kwargs={"pk": self.school.id})
		self.URL_SETTINGS_FORMAT = reverse("school:settings", kwargs={"pk": self.school.id})
		self.URL_OFFICE_HOUR = reverse("school:office-hour", kwargs = {"pk": self.school.id})
		self.URL_OFFICE_HOUR_DETAL = reverse("school:office-hour-detail", kwargs = {"pk": self.office_hour.id})
		self.URL_CALENDAR = reverse("school:calendar", kwargs={"pk": self.school.id})
		self.URL_CALENDAR_DETAIL = reverse("school:calendar-detail", kwargs={"pk": self.calendar.id})
		self.URL_SOCIAL_MEDIA = reverse("school:social-media", kwargs={"pk": self.school.id}) 
		self.URL_COORDINATE = reverse("school:coordinate", kwargs={"pk": self.school.id})
		self.URL_GRADE = reverse("school:grade", kwargs={"pk": self.school.id})
		self.URL_GRADE_DETAIL = reverse("school:grade-detail", kwargs={"pk": self.grade.id})
		self.URL_REPOSITORY = reverse("school:repository", kwargs={"pk": self.school.id})
		self.URL_REPOSITORY_DETAIL = reverse("school:repository-detail", kwargs={"pk": self.repository.id})
		self.URL_INFRAESTRUCTURE = reverse("school:infraestructure", kwargs={"pk": self.school.id})
		self.URL_INFRAESTRUCTURE_DETAIL = reverse("school:infraestructure-detail", kwargs={"pk": self.infra.id})
		self.URL_DOWNLOADS = reverse("school:downloads", kwargs={"pk": self.school.id})
		self.URL_DOWNLOADS_DETAIL = reverse("school:downloads-detail", kwargs={"pk": self.downloads.id})
		self.URL_NEWS = reverse("school:news", kwargs={"pk": self.school.id})
		self.URL_NEWS_DETAIL = reverse("school:news-detail", kwargs={"pk": self.news.id})
		self.URL_CULTURAL_EVENTS = reverse("school:cultural-events", kwargs={"pk": self.school.id})
		self.URL_CULTURAL_EVENTS_DETAIL = reverse("school:cultural-events-detail", kwargs={"pk": self.cultual_events.id})
		self.URL_PAYMENT_INFO = reverse("school:payment-info", kwargs={"pk": self.school.id})
		self.URL_CONTACT_INFO = reverse("school:contact-info", kwargs={"pk": self.school.id})
		self.URL_EXTRA_ACTIVITIE = reverse("school:extra-activitie", kwargs={"pk": self.school.id})
		self.URL_EXTRA_ACTIVITIE_DETAIL = reverse("school:extra-activitie-detail", kwargs={"pk": self.extra_activitie.id})


	def test_get_school(self):
		"""
			Validar endpoint school
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
			Validar endpoint school-detail
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
			Intentar acceder a una información que no existe en endpoint school-detail
		"""
		pk_error = 34

		response = self.client.get(
			reverse("school:detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_settings_format(self):
		"""
			Validar endpoint settings
		"""
		colors = [color.color for color in self.settings_format.colors.all()]

		response = self.client.get(self.URL_SETTINGS_FORMAT)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson['colors'], colors)


	def test_get_office_hour(self):
		"""
			Validar endpoint office-hour
		"""

		response = self.client.get(self.URL_OFFICE_HOUR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.office_hour.id)
		self.assertEqual(responseJson["results"][0]["interval_description"], self.office_hour.interval_description)



	def test_get_office_hour_detail(self):
		"""
			Validar endpoint office-hour-detail
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
			Intentar acceder a una información que no existe en endpoint office-hour-detail
		"""
		pk_error = 35

		response = self.client.get(
			reverse("school:office-hour-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_calendar(self):
		"""
			Validar endpoint calendar 
		"""
		response = self.client.get(self.URL_CALENDAR)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.calendar.id)
		self.assertEqual(responseJson["results"][0]["title"], self.calendar.title)


	def test_get_calendar_detail(self):
		"""
			Validar endpoint calendar-detail
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
			Intentar acceder a una información que no existe en endpoint calendar-detail
		"""
		pk_error = 26

		response = self.client.get(
			reverse("school:calendar-detail", kwargs={"pk": pk_error})
		)

		responseJson = response.data
		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 404)


	def test_get_social_media(self):
		"""
			Validar endpoint social-media
		"""
		response = self.client.get(self.URL_SOCIAL_MEDIA)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson[0]["profile"], self.social_media.profile)


	def get_coordinate(self):
		"""
			Validar endpoint coordinate
		"""
		response = self.client.get(self.URL_COORDINATE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson[0]["title"], self.coordinate.title)
		self.assertEqual(responseJson[0]["latitude"], self.coordinate.latitude)
		self.assertEqual(responseJson[0]["longitude"], self.coordinate.longitude)


	def test_get_grade(self):
		"""
			Validar endpoint grade
		"""
		response = self.client.get(self.URL_GRADE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)

		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.grade.id)
		self.assertEqual(responseJson["results"][0]["name"], self.grade.name)
		self.assertEqual(responseJson["results"][0]["type"], self.grade.type)
		self.assertEqual(responseJson["results"][0]["section"], self.grade.section)


	def test_get_grade_detail(self):
		"""
			Validar endpoint grade-detail
		"""
		teachers = [
			{
				"id": teacher.id, 
				"name": teacher.name,
				"occupation": teacher.occupation
			} 
			for teacher in self.grade.teacher.all()
		]
		response = self.client.get(self.URL_GRADE_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertEqual(responseJson["name"], self.grade.name)
		self.assertEqual(responseJson["description"], self.grade.description)
		self.assertEqual(responseJson["type"], self.grade.type)
		self.assertEqual(responseJson["section"], self.grade.section)
		self.assertEqual(responseJson["teacher"], teachers)	


	def test_get_grade_detail_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint grade-detail
		"""
		pk_error = 12

		response = self.client.get(
			reverse("school:grade-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_repository(self):
		"""
			Validar endpoint repository
		"""
		response = self.client.get(self.URL_REPOSITORY)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.repository.id)
		self.assertEqual(responseJson["results"][0]["name_project"], self.repository.name_project)



	def test_get_repository_detail(self):
		"""
			Validar endpoint repository-detail
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
			Intentar acceder a una información que no existe en endpoint repository-detail
		"""
		pk_error = 45

		response = self.client.get(
			reverse("school:repository-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_infraestructure(self):
		"""
			Validar endpoint infraestructure
		"""
		response = self.client.get(self.URL_INFRAESTRUCTURE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.infra.id)
		self.assertEqual(responseJson["results"][0]["name"], self.infra.name)		
	
	def test_get_infraestructure_detail(self):
		"""
			Validar endpoint infraestructure-detail
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
			Intentar acceder a una información que no existe en endpoint infraestructure-detail
		"""
		pk_error = 45

		response = self.client.get(
			reverse(
				"school:infraestructure-detail",
				kwargs={"pk": pk_error}
			)
		)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 404)


	def test_get_downloads(self):
		"""
			Validar endpoint downloads
		"""
		response = self.client.get(self.URL_DOWNLOADS)
		
		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.downloads.id)
		self.assertEqual(responseJson["results"][0]["title"], self.downloads.title)
		self.assertEqual(responseJson["results"][0]["file"], self.downloads.file)


	def test_get_downloads_detail(self):
		"""
			Validar endpoint downloads-detail
		"""
		response = self.client.get(self.URL_DOWNLOADS_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.downloads.id)
		self.assertEqual(responseJson["title"], self.downloads.title)
		self.assertEqual(responseJson["file"], self.downloads.file)


	def test_get_downloads_detail_does_not_exists(self):
		"""
			Intentar acceder a una información que no existe en endpoint downloads-detail
		"""
		pk_error = 12

		response = self.client.get(
			reverse("school:downloads-detail", kwargs = {"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_news(self):
		"""
			Validar endpoint news
		"""
		response = self.client.get(self.URL_NEWS)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.news.id)
		self.assertEqual(responseJson["results"][0]["title"], self.news.title)


	def test_get_news_detail(self):
		"""
			Validar endpoint news-detail
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
			Intentar acceder a una información que no existe en endpoint news-detail
		"""
		pk_error = 12

		response = self.client.get(
			reverse("school:news-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 404)


	def test_get_cultura_event(self):
		"""
			Validar endpoint cultura-events
		"""
		response = self.client.get(self.URL_CULTURAL_EVENTS)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.cultual_events.id)
		self.assertEqual(responseJson["results"][0]["title"], self.cultual_events.title)



	def test_get_cultura_event_detail(self):
		"""
			Validar endpoint cultura-events-detail
		"""
		response = self.client.get(self.URL_CULTURAL_EVENTS_DETAIL)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.cultual_events.id)
		self.assertEqual(responseJson["title"], self.cultual_events.title)
		self.assertEqual(responseJson["description"], self.cultual_events.description)


	def test_get_cultural_event_detail_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint cultura-events-detail
		"""
		pk_error = 200

		response = self.client.get(
			reverse("school:cultural-events-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_payment_info(self):
		"""
			Validar endpoint payment-info
		"""
		response = self.client.get(self.URL_PAYMENT_INFO)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.payment_info.id)
		self.assertEqual(responseJson["title"], self.payment_info.title)
		self.assertEqual(responseJson["photo"], self.payment_info.photo)
		self.assertEqual(responseJson["description"], self.payment_info.description)


	def test_get_payment_info_with_school_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint payment-info
		"""
		school_pk_error = 45

		response = self.client.get(
			reverse("school:payment-info", kwargs={"pk": school_pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)


	def test_get_contact_info(self):
		"""
			Validar endpoint contact-info
		"""
		response = self.client.get(self.URL_CONTACT_INFO)
		
		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["email"], self.contact_info.email)
		self.assertEqual(responseJson["results"][0]["phone"], self.contact_info.phone)


	def test_get_extra_activitie(self):
		"""
			Validar endpoint extra-activitie
		"""
		response = self.client.get(self.URL_EXTRA_ACTIVITIE)

		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertIn("count", responseJson)
		self.assertIn("next", responseJson)
		self.assertIn("previous", responseJson)
		self.assertEqual(responseJson["results"][0]["id"], self.extra_activitie.id)
		self.assertEqual(responseJson["results"][0]["title"], self.extra_activitie.title)


	def test_get_extra_activitie_detail(self):
		"""
			Validar endpoint extra-activitie-detail
		"""
		response = self.client.get(self.URL_EXTRA_ACTIVITIE_DETAIL)
		
		responseStatus = response.status_code
		responseJson = response.data

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.extra_activitie.id)
		self.assertEqual(responseJson["title"], self.extra_activitie.title)
		self.assertEqual(responseJson["description"], self.extra_activitie.description)


	def test_get_extra_activitie_detail_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint extra-activitie-detail
		"""
		pk_error = 23

		response = self.client.get(
			reverse("school:extra-activitie-detail", kwargs={"pk": pk_error})
		)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)