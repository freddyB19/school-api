import datetime

from rest_framework import status as status_code
from pydantic import validate_call, ConfigDict

from faker import Faker

from apps.school import models
from apps.utils.result_commands import ResultCommand

from .utils.functions import set_name_file
from .utils.errors_messages import SchoolErrorsMessages, TimeGroupErrorsMessages
from .utils.props import (
	NewsParam,
	DjangoDict,
	UploadedFile,
	CalendarParam,
	TimeGroupParam,
	TimeGroupByIdParam,
	OfficeHourParam,
	CoordinateParam,
	ListUploadedFile,
	ProfileURL,
	IsProfileURL,
	ListProfileURL,
	Profile,
	StaffParam,
	GradeValidateParam,
	GradeParam,
	RepositoryParam,
)

faker = Faker(locale="es")


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def update_school_logo(image:UploadedFile = None) -> ResultCommand:
	context = {
		"status": False,
	}

	if not image:
		context.update({"errors": ["Debe pasar una imagen"]})
	
	# Conectarme a un servicio para subir la imagen

	context.update({"query": faker.image_url(), "status": True})

	return ResultCommand(**context)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_school_by_id(id: int) -> ResultCommand:
	school = models.School.objects.filter(id = id).first()
	
	if not school:
		return ResultCommand(
			status = False,
			errors = [{"message": SchoolErrorsMessages.DoesNotExist}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)
		
	return ResultCommand(
		status = True, 
		query = school
	)
	


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def add_newsmedia(media: ListUploadedFile) -> models.NewsMedia:
	# Conectarme a un servicio para subir la imagen
	upload_images = [
		{
			"title": set_name_file(file_name = image.name),
			"photo": faker.image_url()
		}
		for image in media
	]
	# Simulamos: 
	# Cambiar el nombre de los archivos 
	# El resultado de la carga de imagenes
	# Obtener la url del archivo almacenado

	newsmedia = [
		models.NewsMedia(
			title = image.get("title"),
			photo = image.get("photo")
		)
		for image in upload_images
	]

	return models.NewsMedia.objects.bulk_create(newsmedia)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def add_news(news:NewsParam, school_id:int) -> models.News:
	return models.News.objects.create(
		title = news.title,
		description = news.description,
		school_id = school_id,
		status = news.status or models.News.TypeStatus.published
	)


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def create_news(school_id: int, news:NewsParam, images:ListUploadedFile | None = None) -> ResultCommand:
	
	context = {
		"status": False,
	}

	command = get_school_by_id(id = school_id)

	if not command.status:
		return command
	
	news_created = add_news(news = news, school_id = school_id)

	if images:
		news_created.media.set( 
			add_newsmedia(media = images) 
		)

	context.update({"query": news_created, "status": True})

	return ResultCommand(**context)


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def update_news_media(images:ListUploadedFile = None) -> ResultCommand:
	context = {
		"status": False,
	}

	if not images:
		context.update({
			"errors": ["Debe pasar por lo menos una imagen"],
			"error_code": status_code.HTTP_400_BAD_REQUEST
		})
	
	# Conectarme a un servicio para subir la imagen
	total_images = len(images)
	upload_images = [
		models.NewsMedia(photo = faker.image_url()) 
		for _ in range(total_images)
	]

	newsmedia = models.NewsMedia.objects.bulk_create(upload_images)

	context.update({"query": newsmedia, "status": True})

	return ResultCommand(**context)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def add_time_group(time_group: TimeGroupParam) -> models.TimeGroup:
	days = time_group.daysweek

	time_group = models.TimeGroup.objects.create(
		type = time_group.type,
		opening_time = time_group.opening_time,
		closing_time = time_group.closing_time,
		active = time_group.active,
		overview = time_group.overview,
	)

	if days:
		daysweek = models.DaysWeek.objects.filter(day__in = days)
		time_group.daysweek.set(daysweek)
	
	return time_group

@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def add_office_hour(school_id: int, description: str) -> models.OfficeHour:
	return models.OfficeHour.objects.create(
		school_id = school_id,
		interval_description = description
	)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_or_create_time_group(time_group: TimeGroupParam | TimeGroupByIdParam) -> models.TimeGroup | None:
	if isinstance(time_group, TimeGroupParam):
		return add_time_group(time_group)
	return models.TimeGroup.objects.filter(id = time_group.id).first()


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_office_hour(school_id: int, office_hour: OfficeHourParam) -> ResultCommand:
	
	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	time_group =  get_or_create_time_group(time_group = office_hour.time_group)

	if not time_group:
		return ResultCommand(
			status = False, 
			errors = [{"message": TimeGroupErrorsMessages.DOES_NOT_EXIST}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)

	officehour = add_office_hour(school_id = school_id, description = office_hour.description)
	
	officehour.time_group = time_group
	officehour.save()

	return ResultCommand(**{"query": officehour, "status": True})

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_calendar(school_id:int, calendar: CalendarParam) -> ResultCommand:

	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	calendar = models.Calendar.objects.create(
		school_id = school_id,
		title = calendar.title,
		description = calendar.description,
		date = calendar.date
	)

	return ResultCommand(query = calendar, status = True)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def calendar_exist(school_id: int, title: str, date: datetime.date) -> ResultCommand:
	
	result = models.Calendar.objects.filter(
		school_id = school_id,
		title = title,
		date = date
	).exists()

	return ResultCommand(query = result, status = True)

formatValueURL = lambda url: [url] if isinstance(url, IsProfileURL) else url

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def social_media_exist(school_id, social_network: Profile) -> ResultCommand:

	search_social_network = formatValueURL(url = social_network)

	result = models.SocialMedia.objects.filter(
		school_id = school_id,
		profile__in = search_social_network
	).exists()

	return ResultCommand(query = result, status = True)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def bulk_add_social_media(school_id, profiles: ListProfileURL) -> list[models.SocialMedia]:
	
	social_media = [
		models.SocialMedia(
			school_id = school_id,
			profile = profile
		) 
		for profile in profiles
	]

	return models.SocialMedia.objects.bulk_create(social_media)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def add_social_media(school_id: int, profile: ProfileURL):
	return models.SocialMedia.objects.create(
		school_id = school_id, 
		profile = profile
	)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def save_social_media(school_id: int, social_network: Profile) -> list[models.SocialMedia] | models.SocialMedia:
	if isinstance(social_network, IsProfileURL):
		return add_social_media(school_id = school_id, profile = social_network)
	return bulk_add_social_media(school_id = school_id, profiles = social_network)
	
@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_social_media(school_id: int, social_network: Profile) -> ResultCommand:

	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	social_media = save_social_media(
		school_id = school_id, 
		social_network = social_network
	)

	return ResultCommand(query = social_media, status = True)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def coordinate_exist(school_id: int, coordinate: CoordinateParam) -> ResultCommand:

	exist = models.Coordinate.objects.filter(
		school_id = school_id,
		title = coordinate.title,
		latitude = coordinate.latitude,
		longitude = coordinate.longitude,
	).exists()

	return ResultCommand(query = exist, status = True)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_coordinate(school_id: int, coordinate: CoordinateParam) -> ResultCommand:
	command = get_school_by_id(id = school_id)

	if not command.status:
		return command
	
	coordinate = models.Coordinate.objects.create(
		school_id = school_id,
		title = coordinate.title,
		latitude = coordinate.latitude,
		longitude = coordinate.longitude,
	)

	return ResultCommand(query = coordinate, status = True)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_administrative_staff(school_id: int, admins: list[int]) -> models.SchoolStaff:
	return models.SchoolStaff.objects.filter(
		id__in = admins,
		school_id = school_id,
		occupation = models.OccupationStaff.administrative
	)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_staff(school_id: int, staff: StaffParam) -> ResultCommand:
	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	staff = models.SchoolStaff.objects.create(
		school_id = school_id,
		name = staff.name,
		occupation = staff.occupation or models.OccupationStaff.administrative
	)

	return ResultCommand(query = staff, status = True)

@validate_call(config=ConfigDict(hide_input_in_errors=True))
def grade_exist(school_id: int, grade: GradeValidateParam) -> ResultCommand:

	exist = models.Grade.objects.filter(
		school_id = school_id,
		section = grade.section,
		level = grade.level,
		stage_id = grade.stage_id,
	).exists()

	return ResultCommand(query = exist, status = True)

@validate_call(config=ConfigDict(hide_input_in_errors=True))
def create_grade(school_id: int, grade: GradeParam) -> ResultCommand:
	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	new_grade = models.Grade.objects.create(
		name = grade.name,
		level = grade.level,
		section = grade.section,
		description = grade.description,
		school_id = school_id,
		stage_id = grade.stage_id,
	)

	if grade.teachers:
		new_grade.teacher.set(
			models.SchoolStaff.objects.filter(
				id__in = grade.teachers,
				school_id = school_id,
				occupation = models.OccupationStaff.teacher
			)
		)

	return ResultCommand(query = new_grade, status = True)


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def add_repository_media(media: ListUploadedFile) -> list[models.RepositoryMediaFile]:
	# Conectarme a un servicio para subir los archivos

	upload_files = [
		{
			"title": set_name_file(file_name = file.name),
			"file": f"{faker.url()}{set_name_file(file_name = file.name)}"
		}
		for file in media
	]
	# Simulamos: 
	# Cambiar el nombre de los archivos .
	# El resultado de la carga de archivos.
	# Obtener la url del archivo almacenado.

	repository_media = [
		models.RepositoryMediaFile(
			title = file.get("title"),
			file = file.get("file")
		)
		for file in upload_files
	]

	return models.RepositoryMediaFile.objects.bulk_create(repository_media)

@validate_call(config=ConfigDict(hide_input_in_errors=True))
def repository_exist(school_id: int, name_project: str) -> ResultCommand:

	exist = models.Repository.objects.filter(
		school_id = school_id,
		name_project = name_project
	).exists()

	return ResultCommand(query = exist, status = True)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_repository(school_id: int, repository: RepositoryParam) -> ResultCommand:
	command = get_school_by_id(id = school_id)

	if not command.status:
		return command

	new_repository = models.Repository.objects.create(
		school_id = school_id,
		name_project = repository.name_project,
		description = repository.description
	)

	if repository.media:
		new_repository.media.set(
			add_repository_media(media = repository.media)
		)

	return ResultCommand(query = new_repository, status = True) 
