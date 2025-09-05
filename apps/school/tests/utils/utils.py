import datetime

from faker import Faker

faker = Faker(locale="es")

from apps.school import models

def create_dayweek():
	dayweek = ( 1,2,3,4,5 )

	day = faker.random_element(elements = dayweek)

	return models.DaysWeek.objects.create(day = day)


def create_school(**kwargs):
	data = {
		"name": faker.name(),
		"subdomain": faker.domain_word(),
		"logo": faker.image_url(),
		"address": faker.address(),
		"mission": faker.paragraph(),
		"vision": faker.paragraph(),
		"history": faker.paragraph(),
		"private": faker.random_element(elements = (True, False))
	}

	data.update(kwargs)

	return models.School.objects.create(**data)


def create_color_hex_format():
	"""
		Nos permite crear multiples registros en una sola consulta
		
		Argumentos:
		(Sin argumentos)
		
		Retorno:
		Lista de colores creados
	"""
	
	colors = [
		models.ColorHexFormat(color = faker.hex_color())
		for _ in range(5)
	]
	
	return models.ColorHexFormat.objects.bulk_create(colors)


def create_time_group(**kwargs):
	data = {
		"type": faker.text(max_nb_chars = 20),
		"opening_time": faker.date_time(),
		"closing_time": faker.date_time(),
		"active": faker.random_element(elements = (True, False)),
		"overview": faker.paragraph()
	}

	data.update(kwargs)

	time_group = models.TimeGroup.objects.create(**data)

	time_group.daysweek.add(models.DaysWeek.objects.create(day = 2))

	return time_group


def create_office_hour(id, **kwargs):
	data = {
		"interval_description": faker.text(max_nb_chars = 20)
	}

	data.update(kwargs)

	time_group = create_time_group()

	office_hour = models.OfficeHour.objects.create(
		school_id = id, 
		time_group_id = time_group.id, 
		**data
	)

	return office_hour

def create_calendar(id, **kwargs):
	date = datetime.datetime.now()
	februry = 2
	month = date.month

	start_day = 1
	end_day = 28 if month == februry else 30

	data = {
		"title": faker.text(max_nb_chars=20),
		"description": faker.paragraph(),
		"date": faker.date_time_between(
			start_date = datetime.date(date.year, date.month, start_day),
			end_date = datetime.date(date.year, date.month, end_day)
		),
	}
	
	data.update(kwargs)

	return models.Calendar.objects.create(school_id = id, **data)


def create_social_media(id, **kwargs):
	data = {
		"profile": faker.url()
	}
	
	data.update(kwargs)

	return models.SocialMedia.objects.create(school_id = id, **data)


def create_coordinate(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars=20),
		"latitude": faker.local_latlng(country_code = 'VE')[0],
		"longitude": faker.local_latlng(country_code = 'VE')[1],
	}
	return models.Coordinate.objects.create(school_id = id, **data)


def create_school_staff(id, **kwargs):
	data = {
		"name": faker.name(),
		"occupation": faker.random_element(elements = ("profesor", "administrativo")),
	}

	data.update(kwargs)

	return models.SchoolStaff.objects.create(school_id = id, **data)


def create_grade(id, **kwargs):

	data = {
		"name": f"{faker.random_element(elements = (1,2,3,4,5))}º {faker.random_element(elements = ('grado', 'año'))}",
		"description": faker.paragraph(),
		"type": faker.random_element(elements = ("preescolar", "básica", "secundaria")),
		"section": "".join(faker.random_letters(length = 3))
	}

	data.update(kwargs)

	grade = models.Grade.objects.create(school_id = id, **data)

	grade.teacher.add(create_school_staff(id = id, occupation="profesor"))

	return grade


def create_media_respository(**kwargs):
	data = {
		"title": faker.text(max_nb_chars=20),
		"file": f"{faker.url()}{faker.file_path(category = 'office')[1:]}"
	}
	data.update(kwargs)
	return models.RepositoryMediaFile.objects.create(**data)


def create_repository(id, **kwargs):
	data = {
		"name_project": faker.text(max_nb_chars = 20),
		"description": faker.paragraph(),
	}

	data.update(kwargs)

	repository = models.Repository.objects.create(school_id = id, **data)

	repository.media.add(create_media_respository())

	return repository

def create_infraestructure_media(**kwargs):
	data = {
		"title": faker.name(),
		"photo": faker.image_url(),
	}

	data.update(kwargs)

	return models.InfraestructureMedia.objects.create(**data)

def create_infraestructure(id, **kwargs):
	data = {
		"name": faker.name(),
		"description": faker.paragraph()
	}

	data.update(kwargs)

	infra = models.Infraestructure.objects.create(school_id = id, **data)

	infra.media.add(create_infraestructure_media())

	return infra


def create_download(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars=20),
		"file": f"{faker.url()}{faker.file_path(category = 'office')[1:]}",
		"description": faker.paragraph()
	}

	data.update(kwargs)

	return models.Download.objects.create(school_id = id, **kwargs)


def create_news_media(**kwargs):
	data = {
		"title": faker.name(),
		"photo": faker.image_url()
	}

	data.update(kwargs)

	return models.NewsMedia.objects.create(**data)

def create_news(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"description": faker.paragraph(),
		"status": faker.random_element(elements = ("pendiente", "publicado")),
	}

	data.update(kwargs)

	news = models.News.objects.create(school_id = id, **data)

	news.media.add(create_news_media())

	return news


def bulk_create_news(id: int) -> list[models.News]:
	news = [
		models.News(
			school_id = id,
			title = faker.text(max_nb_chars = 20),
			description =  faker.paragraph(),
			status = faker.random_element(elements = models.News.TypeStatus.values)
		)

		for _ in range(5)
	]

	return models.News.objects.bulk_create(news)



def create_cultura_event_media(**kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"photo": faker.image_url()
	}

	data.update(kwargs)

	return models.CulturalEventMedia.objects.create(**data)


def create_cultura_event(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"description": faker.paragraph(),
		"date": faker.date_time()
	}

	data.update(kwargs)

	cultural_event = models.CulturalEvent.objects.create(school_id = id, **data)

	cultural_event.media.add(create_cultura_event_media())

	return cultural_event


def create_payment_info(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"photo": faker.image_url(),
		"description": faker.paragraph()
	}

	data.update(kwargs)

	return models.PaymentInfo.objects.create(school_id = id, **data)


def create_payment_report(id, grade_id, **kwargs):
	data = {
		"fullname_student": faker.name(),
		"payment_detail": faker.url(),
	}

	data.update(kwargs)

	return models.PaymentReport.objects.create(school_id = id, grade_id = grade_id, **data)


def create_contac_info(id, **kwargs):
	data = {
		"email": faker.email(),
		"phone": f"{faker.random_number(digits = 11, fix_len = True)}"
	}

	data.update(kwargs)

	return models.ContactInfo.objects.create(school_id = id, **data)


def create_extra_activitie_schedule(**kwargs):
	data = {
		"type": faker.text(max_nb_chars  = 20),
		"opening_time": faker.date_time(),
		"closing_time": faker.date_time(),
		"active": faker.random_element(elements = (True, False)) 
	}

	data.update(kwargs)

	extra_act_schedule = models.ExtraActivitieSchedule.objects.create(**data)

	extra_act_schedule.daysweek.add(models.DaysWeek.objects.create(day = 1))

	return extra_act_schedule


def create_extra_activitie_files(**kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"file": f"{faker.url()}{faker.file_path(category = 'office')[1:]}",
	}

	data.update(kwargs)

	return models.ExtraActivitieFile.objects.create(**data)

def create_extra_activitie_photos(**kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"photo": faker.image_url(),
	}

	data.update(kwargs)

	return models.ExtraActivitiePhoto.objects.create(**data)

def create_extra_activitie(id, **kwargs):
	data = {
		"title": faker.text(max_nb_chars = 20),
		"description": faker.paragraph()
	}

	data.update(kwargs)

	extra_act = models.ExtraActivitie.objects.create(school_id = id, **data)

	extra_act.schedules.add(create_extra_activitie_schedule())
	extra_act.files.add(create_extra_activitie_files())
	extra_act.photos.add(create_extra_activitie_photos())

	return extra_act