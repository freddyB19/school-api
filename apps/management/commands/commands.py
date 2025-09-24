from typing import Optional

from rest_framework import status as status_code
from pydantic import validate_call, ConfigDict

from faker import Faker

from apps.school import models
from apps.utils.result_commands import ResultCommand, BaseMessage
from apps.utils.decorators import handler_validation_errors

from .utils.functions import set_name_image
from .utils.errors_messages import SchoolErrorsMessages
from .utils.props import (
	NewsParam,
	DjangoDict,
	UploadedFile,
	TimeGroupParam,
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
	try:
	
		return ResultCommand(
			status = True, 
			query = models.School.objects.get(id = id)
		)
	
	except models.School.DoesNotExist as e:
		return ResultCommand(
			status = False,
			errors = [{"message": SchoolErrorsMessages.DoesNotExist}],
			error_code = status_code.HTTP_404_NOT_FOUND
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
def update_news_media(images:DjangoDict = None) -> ResultCommand:
	context = {
		"status": False,
	}

	if not images:
		context.update({
			"errors": ["Debe pasar por lo menos una imagen"],
			"error_code": status_code.HTTP_400_BAD_REQUEST
		})
	
	# Conectarme a un servicio para subir la imagen

	upload_images = [models.NewsMedia(photo = faker.image_url()) for _ in range(5)]

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

	officehour = add_office_hour(school_id = school_id, description = office_hour.description)
	officehour.time_group = add_time_group(time_group = office_hour.time_group)
	officehour.save()


	return ResultCommand(**{"query": officehour, "status": True})