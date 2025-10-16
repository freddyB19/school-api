import datetime
from typing import Optional

from rest_framework import status as status_code
from pydantic import validate_call, ConfigDict

from faker import Faker

from apps.school import models
from apps.utils.result_commands import ResultCommand, BaseMessage
from apps.utils.decorators import handler_validation_errors

from .utils.functions import set_name_image
from .utils.errors_messages import SchoolErrorsMessages, TimeGroupErrorsMessages
from .utils.props import (
	NewsParam,
	DjangoDict,
	UploadedFile,
	CalendarParam,
	TimeGroupParam,
	TimeGroupByIdParam,
	OfficeHourParam,
	ListUploadedFile,
	IntervalDescription
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
			"title": set_name_image(image_name = image.name),
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


@handler_validation_errors
def create_news(school_id: int, news:NewsParam, images:ListUploadedFile | None = None, errors:Optional[list[BaseMessage]] = None) -> ResultCommand:
	if errors:
		return ResultCommand(
			status = False, 
			errors = errors, 
			error_code = status_code.HTTP_400_BAD_REQUEST
		)
	
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
def add_office_hour(school_id: int, description: IntervalDescription) -> models.OfficeHour:
	return models.OfficeHour.objects.create(
		school_id = school_id,
		interval_description = description
	)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_or_create_time_group(time_group: TimeGroupParam | TimeGroupByIdParam) -> models.TimeGroup | None:
	if isinstance(time_group, TimeGroupParam):
		return add_time_group(time_group)
	return models.TimeGroup.objects.filter(id = time_group.id).first()


@handler_validation_errors
def create_office_hour(school_id: int, office_hour: OfficeHourParam, errors:Optional[list[BaseMessage]] = None) -> ResultCommand:
	
	if errors:
		return ResultCommand(
			status = False, 
			errors = errors, 
			error_code = status_code.HTTP_400_BAD_REQUEST
		)

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

@handler_validation_errors
def create_calendar(school_id:int, calendar: CalendarParam, errors:list[BaseMessage] | None = None) -> ResultCommand:
	if errors:
		return ResultCommand(
			status = False, 
			errors = errors, 
			error_code = status_code.HTTP_400_BAD_REQUEST
		)

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