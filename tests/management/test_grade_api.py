from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import create_school, bulk_create_school_staff
from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data


def get_list_create_grade_url(school_id):
	return reverse(
		"management:grade-list-create",
		kwargs={"pk": school_id}
	)


class GradeCreateAPITest(testcases.GradeCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_GRADE_CREATE = get_list_create_grade_url(school_id = self.school.id)

		stage = faker.random_element(elements = self.stages)

		self.add_grade = {
			"name": faker.text( max_nb_chars = models.MAX_LENGTH_GRADE_NAME),
			"level": faker.random_int(
				min = models.MIN_LENGTH_GRADE_LEVEL, 
				max = models.MAX_LENGTH_GRADE_LEVEL
			),
			"section": faker.random_letter(),
			"description": faker.paragraph(),
			"stage_id": stage.id
		}

	def test_create_grade(self):
		"""
			Validar "POST /grade" (sin profesores)
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		stage = models.EducationalStage.objects.filter(id = self.add_grade["stage_id"]).first()
		total_teachers = 0
		
		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(responseJson["name"], self.add_grade["name"])
		self.assertEqual(responseJson["level"], self.add_grade["level"])
		self.assertEqual(responseJson["section"], self.add_grade["section"])
		self.assertEqual(responseJson["stage"], stage.type)
		self.assertEqual(responseJson["description"], self.add_grade["description"])
		self.assertEqual(len(responseJson["teacher"]), total_teachers)


		#	Validar "POST /grade" (con profesores)

		total_teachers = 3

		teachers = bulk_create_school_staff(
			school = self.school,
			size = total_teachers, 
			occupation = models.OccupationStaff.teacher
		)

		teachers_id = [teacher.id for teacher in teachers]

		self.add_grade.update({
			"teachers_id": teachers_id,
			"section": faker.random_letter()
		})

		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(len(responseJson["teacher"]), total_teachers)
		self.assertEqual(responseJson["section"], self.add_grade["section"])

	def test_create_grade_with_wrong_staff(self):
		"""
			Generar [Error 400] "POST /grade" por enviar datos invalidos en el campo 'teachers_id'
		"""
		# Generar error por enviar el ID de personal administrativo
		
		self.client.force_authenticate(user = self.user_with_add_perm)

		total_teachers = 2
		total_admins = 3

		teachers = bulk_create_school_staff(
			school = self.school,
			size = total_teachers, 
			occupation = models.OccupationStaff.teacher
		)
		admins = bulk_create_school_staff(
			school = self.school,
			size = total_admins, 
			occupation = models.OccupationStaff.administrative
		)

		teachers_id = [teacher.id for teacher in teachers]
		admins_id = [admin.id for admin in admins]

		staff = teachers_id + admins_id

		self.add_grade.update({
			"teachers_id": staff,
			"section": faker.random_letter()
		})

		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

	def test_create_grade_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /grade" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_case = testcases_data.CREATE_GRADE_WITH_WRONG_DATA
		stage_id = self.add_grade["stage_id"]
		
		for case in test_case:
			with self.subTest(case = case):
				case.update({"stage_id": stage_id})
				response = self.client.post(
					self.URL_GRADE_CREATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

	def test_create_grade_without_school_permission(self):
		"""
			Generar [Error 403] "POST /grade" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()
		
		response = self.client.post(
			get_list_create_grade_url(school_id = other_school.id),
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_grade_without_user_permission(self):
		"""
			Generar [Error 403] "POST /grade" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_grade_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /grade" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["add_grade"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_grade_without_authentication(self):
		"""
			Generar [Error 401] "POST /grade" sin autenticación
		"""
		response = self.client.post(
			self.URL_GRADE_CREATE,
			self.add_grade
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)
