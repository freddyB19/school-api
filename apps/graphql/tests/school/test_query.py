import json, datetime

from graphene_django.utils.testing import GraphQLTestCase

from apps.school.tests.utils.utils import (
	create_school,
	create_settings_format,
	create_calendar,
	create_social_media,
	create_coordinate,
	create_grade,
	create_repository,
	create_infraestructure,
	create_download,
	create_news,
)


class SchoolQueryTest(GraphQLTestCase):
	def setUp(self):
		self.school = create_school()

		settings = create_settings_format(id = self.school.id)
		self.settings_colors = [data.color for data in settings.colors.all()]

		self.calendar = create_calendar(id = self.school.id, date = datetime.datetime.utcnow())
		self.networks = create_social_media(id = self.school.id)
		self.news = create_news(id = self.school.id)
		self.coordinate = create_coordinate(id = self.school.id)
		self.repository = create_repository(id = self.school.id)
		self.infra = create_infraestructure(id = self.school.id)
		self.downloads = create_download(id = self.school.id)

		self.query_schoolBySubdomain = """
			query School($subdomain: String!) {
				schoolBySubdomain(subdomain: $subdomain) {
					school {
						id
						name
						subdomain
					}
					
					settings {
						color
					}

					calendar {
						title
					}

					networks {
						profile
					}
					
					news {
						id
						title
					}

					coordinates {
						id
						title
					}

				}
			}
		"""

		self.variables_schoolBySubdomain = {
			"subdomain": self.school.subdomain
		}

		self.query_schoolService = """
			query SchoolService($schoolId: Int!){
				schoolServiceOnline(schoolId: $schoolId) {
					downloads {
						id
						title
					}
					
					repositories {
						id
						project
					}
				}

				schoolServiceOffline(schoolId: $schoolId) {
					infraestructure {
						id
						photo
					}
				}
			}
		"""
		self.variables_schoolService = {
			"schoolId": self.school.id
		}


	def test_get_schoolBySubdomain(self):
		"""
			Obtener la información de una escuela por su 'subdomain'
		"""
		result = self.query(
			self.query_schoolBySubdomain,
			variables = self.variables_schoolBySubdomain
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["school"]["subdomain"],
			self.school.subdomain
		)
		self.assertEqual(
			response["data"]["schoolBySubdomain"]["school"]["name"],
			self.school.name
		)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["settings"]["color"][0],
			self.settings_colors[0]
		)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["news"][0]["id"],
			str(self.news.id)
		)
		self.assertEqual(
			response["data"]["schoolBySubdomain"]["news"][0]["title"],
			self.news.title
		)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["calendar"][0]["title"],
			self.calendar.title
		)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["networks"][0]["profile"],
			self.networks.profile
		)

		self.assertEqual(
			response["data"]["schoolBySubdomain"]["coordinates"][0]["id"],
			str(self.coordinate.id)
		)
		self.assertEqual(
			response["data"]["schoolBySubdomain"]["coordinates"][0]["title"],
			self.coordinate.title
		)


	def test_get_schoolService(self):
		"""
			Obtener la información de los servicios de una escuela
		"""
		result = self.query(
			self.query_schoolService,
			variables = self.variables_schoolService
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		self.assertEqual(
			response["data"]["schoolServiceOnline"]["downloads"][0]["id"],
			str(self.downloads.id)
		)
		self.assertEqual(
			response["data"]["schoolServiceOnline"]["downloads"][0]["title"],
			self.downloads.title
		)
		
		self.assertEqual(
			response["data"]["schoolServiceOnline"]["repositories"][0]["id"],
			str(self.repository.id)
		)

		self.assertEqual(
			response["data"]["schoolServiceOnline"]["repositories"][0]["project"],
			self.repository.name_project
		)

		self.assertEqual(
			response["data"]["schoolServiceOffline"]["infraestructure"][0]["id"],
			str(self.infra.id)
		)
		self.assertEqual(
			response["data"]["schoolServiceOffline"]["infraestructure"][0]["photo"],
			self.infra.media.first().photo
		)
