from django.urls import reverse

from apps.school import models

from tests import faker
from tests.school.utils import (
	create_school, 
	create_grade,
	bulk_create_grade,
	bulk_create_school_staff
)
from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data


def get_list_create_grade_url(school_id, **extra):
	return reverse(
		"management:grade-list-create",
		kwargs={"pk": school_id},
		**extra
	)

def get_detail_grade_url(id):
	return reverse(
		"management:grade-detail",
		kwargs={"pk": id}
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


class GradeListAPITest(testcases.GradeTestCase):
	def setUp(self):
		super().setUp()
		
		#Preescolar
		bulk_create_grade(size = 3, stage = self.dic_stages["preescolar"], school = self.school)

		#Primaria
		bulk_create_grade(size = 2, level = 1, stage = self.dic_stages["basica"], school = self.school)
		bulk_create_grade(size = 2, level = 2, stage = self.dic_stages["basica"], school = self.school)
		bulk_create_grade(size = 2, level = 3, stage = self.dic_stages["basica"], school = self.school)
		bulk_create_grade(size = 2, level = 4, stage = self.dic_stages["basica"], school = self.school)
		bulk_create_grade(size = 3, level = 5, stage = self.dic_stages["basica"], school = self.school)
		bulk_create_grade(size = 3, level = 6, stage = self.dic_stages["basica"], school = self.school)
		
		#Bachillerato
		bulk_create_grade(size = 2, level = 1, stage = self.dic_stages["secundaria"], school = self.school)
		bulk_create_grade(size = 2, level = 2, stage = self.dic_stages["secundaria"], school = self.school)
		bulk_create_grade(size = 2, level = 3, stage = self.dic_stages["secundaria"], school = self.school)
		bulk_create_grade(size = 2, level = 4, stage = self.dic_stages["secundaria"], school = self.school)
		bulk_create_grade(size = 3, level = 5, stage = self.dic_stages["secundaria"], school = self.school)
		
		self.URL_GRADE_LIST = get_list_create_grade_url(school_id = self.school.id)

	def test_get_grade(self):
		"""
			Validar "GET /grade"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_grade = models.Grade.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_GRADE_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade, responseJson["count"])

	def test_get_grade_by_filter_stage_type(self):
		"""
			Validar "GET /grade?stage=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		stage_preschool = models.TypeEducationalStageByNumber.preschool
		stage_primary = models.TypeEducationalStageByNumber.primary
		stage_high = models.TypeEducationalStageByNumber.high

		total_grade_by_stage_preschool = models.Grade.objects.filter(
			school_id = self.school.id,
			stage__type_number = stage_preschool
		).count()

		total_grade_by_stage_primary = models.Grade.objects.filter(
			school_id = self.school.id,
			stage__type_number = stage_primary
		).count()
		
		total_grade_by_stage_high = models.Grade.objects.filter(
			school_id = self.school.id,
			stage__type_number = stage_high
		).count()

		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"stage": stage_preschool}
			)		
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_stage_preschool, responseJson["count"])

		#
		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"stage": stage_primary}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_stage_primary, responseJson["count"])

		#
		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"stage": stage_high}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_stage_high, responseJson["count"])

	def test_get_grade_by_filter_level(self):
		"""
			Validar "GET /grade?level=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		search_stage = models.TypeEducationalStageByNumber.high

		search_level = faker.random_int(min = models.MIN_LENGTH_GRADE_LEVEL, max = models.MAX_LENGTH_GRADE_LEVEL)

		bulk_create_grade(size = 2, school = self.school, stage = self.dic_stages["secundaria"], level = search_level)

		total_grade_by_level = models.Grade.objects.filter(
			school_id = self.school.id,
			level = search_level,
			stage__type_number = search_stage,
		).count()

		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"level": search_level, "stage": search_stage}
			)
			
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_level, responseJson["count"])

	def test_get_grade_by_filter_section(self):
		"""
			Validar "GET /grade?section=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		search_section = faker.random_letter()
		search_stage = models.TypeEducationalStageByNumber.primary

		bulk_create_grade(size = 1, level = 2, section = search_section, stage = self.dic_stages["basica"] ,school = self.school)
		
		total_grade_by_section = models.Grade.objects.filter(
			school_id = self.school.id,
			section = search_section,
			stage__type_number = search_stage,
		).count()

		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"section": search_section, "stage": search_stage}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_section, responseJson["count"])

		#
		models.Grade.objects.create( # grado sin una 'sección'
			school_id = self.school.id,
			level = 1,
			stage_id = self.dic_stages["preescolar"].id,
			name = faker.text(max_nb_chars = models.MAX_LENGTH_GRADE_NAME)
		)
		search_stage = models.TypeEducationalStageByNumber.preschool
		unsection = True
		total_grade_by_section_null = models.Grade.objects.filter(
			school_id = self.school.id,
			stage__type_number = search_stage,
			section__isnull = unsection
		).count()

		response = self.client.get(
			get_list_create_grade_url(
				school_id = self.school.id,
				query = {"unsection": unsection, "stage": search_stage}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(total_grade_by_section_null, responseJson["count"])

	def test_get_grade_without_school_permission(self):
		"""
			Generar [Error 403] "GET /grade" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_list_create_grade_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)


	def test_get_grade_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /grade" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		
		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_GRADE_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_get_grade_without_authentication(self):
		"""
			Generar [Error 401] "GET /grade" sin autenticación
		"""
		response = self.client.get(self.URL_GRADE_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class GradeDetailAPITest(testcases.GradeDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.grade = create_grade(school = self.school)

		self.URL_GRADE_DETAIL = get_detail_grade_url(id = self.grade.id)

	def test_detail_grade(self):
		"""
			Validar "GET /grade/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_GRADE_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertEqual(responseJson["name"], self.grade.name)
		self.assertEqual(responseJson["description"], self.grade.description)
		self.assertEqual(responseJson["level"], self.grade.level)
		self.assertEqual(responseJson["section"], self.grade.section)
		self.assertEqual(responseJson["stage"], self.grade.stage.type)
		self.assertEqual(len(responseJson["teacher"]), self.grade.teacher.count())

	def test_detail_grade_without_school_permission(self):
		"""
			Generar [Error 403] "GET /grade/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_grade = create_grade()

		response = self.client.get(
			get_detail_grade_url(id = other_grade.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_detail_grade_wrong_user(self):
		"""
			Generar [Error 403] "GET /grade/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_GRADE_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_detail_grade_without_authentication(self):
		"""
			Generar [Error 401] "GET /grade/:id" sin autenticación
		"""
		response = self.client.get(self.URL_GRADE_DETAIL)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class GradeDeleteAPITest(testcases.GradeDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.grade = create_grade(school = self.school)

		self.URL_GRADE_DELETE = get_detail_grade_url(id = self.grade.id)

	def test_delete_grade(self):
		"""
			Validar "DELETE /grade/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_GRADE_DELETE)
		
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 204)

	def test_delete_grade_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /grade/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		other_grade = create_grade()

		response = self.client.delete(
			get_detail_grade_url(id = other_grade.id)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_grade_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /grade/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)
		
		response = self.client.delete(self.URL_GRADE_DELETE)
		
		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_grade_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /grade/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_grade"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_GRADE_DELETE)
		
		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_delete_grade_without_authentication(self):
		"""
			Generar [Error 400] "DELETE /grade/:id" sin autenticación
		"""
		response = self.client.delete(self.URL_GRADE_DELETE)
		
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class GradeUpdateAPITest(testcases.GradeDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.grade = create_grade(school = self.school)

		self.URL_GRADE_UPDATE = get_detail_grade_url(id = self.grade.id)

		self.partial_update = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_GRADE_NAME),
			"section": faker.random_letter()
		}
		
		stage = faker.random_element(elements = self.stages)
		teachers = bulk_create_school_staff(
			size = 1, 
			school = self.school,
			occupation = models.OccupationStaff.teacher
		)

		teacher_id = map(lambda teacher: teacher.id, teachers)

		self.update = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_GRADE_NAME),
			"level": faker.random_int(
				min = models.MIN_LENGTH_GRADE_LEVEL, 
				max = models.MAX_LENGTH_GRADE_LEVEL
			),
			"section": faker.random_letter(),
			"description": faker.paragraph(),
			"stage_id": stage.id,
			"teacher": teacher_id
		}

	def test_update_grade(self):
		"""
			Validar "PUT/PATCH /grade/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			self.partial_update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertNotEqual(responseJson["name"], self.grade.name)
		self.assertNotEqual(responseJson["section"], self.grade.section)

		response = self.client.put(
			self.URL_GRADE_UPDATE,
			self.update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertEqual(responseJson["name"], self.update["name"])
		self.assertEqual(responseJson["level"], self.update["level"])
		self.assertEqual(responseJson["section"], self.update["section"])
		self.assertEqual(responseJson["description"], self.update["description"])

		# Update 'teacher'
		teachers = bulk_create_school_staff(
			size = 2, 
			school = self.school,
			occupation = models.OccupationStaff.teacher
		)

		teachers_id = list(map(lambda teacher: teacher.id, teachers))

		partial_update_teacher = {"teacher": teachers_id}

		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			partial_update_teacher
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["id"], self.grade.id)
		self.assertEqual(
			len(responseJson["teacher"]), 
			len(list(partial_update_teacher["teacher"]))
		)

	def test_update_grade_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /grade/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_case = testcases_data.CREATE_GRADE_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_GRADE_UPDATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

	def test_update_grade_with_data_already_exist(self):
		"""
			Generar [Error 400] "PUT/PATCH /grade/:id" por enviar datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		grade = create_grade(school = self.school)

		update = {
			"level" : grade.level,
			"section":  grade.section,
			"stage" : grade.stage.id
		}

		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

	def test_update_grade_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /grade/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		other_grade = create_grade()

		response = self.client.patch(
			get_detail_grade_url(id = other_grade.id),
			self.partial_update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_grade_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /grade/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			self.partial_update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_grade_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /grade/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_grade"])
		)
		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			self.partial_update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_update_grade_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /grade/:id" sin autenticación
		"""
		response = self.client.patch(
			self.URL_GRADE_UPDATE,
			self.partial_update
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)
