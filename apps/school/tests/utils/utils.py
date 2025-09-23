import datetime, random

import factory, factory.fuzzy
from faker import Faker

from apps.school import models


faker = Faker(locale="es")

class DaysWeekFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.DaysWeek
		django_get_or_create = ("day", )

	day = factory.LazyAttribute(lambda x: random.choice([1,2,3,4,5]))


def create_daysweek():
	return DaysWeekFactory.create_batch(size = 5)


class SchoolFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.School

	name = faker.name()
	subdomain = factory.LazyAttributeSequence(lambda obj, num: f"{faker.domain_word()}-{num}") 
	logo = faker.image_url()
	address = faker.address()
	mission = faker.paragraph()
	vision = faker.paragraph()
	history = faker.paragraph()
	private = faker.random_element(elements = (True, False))


def create_school(**kwargs) -> models.School:
	return SchoolFactory.create(**kwargs)


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


class TimeGroupBaseFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.TimeGroup

	type = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	opening_time = factory.LazyFunction(lambda: datetime.time(7, 30))
	closing_time = factory.LazyFunction(lambda: datetime.time(17,30))
	active = factory.fuzzy.FuzzyChoice((True, False))
	overview = factory.LazyAttribute(lambda x: faker.paragraph())


class TimeGroupFactory(TimeGroupBaseFactory):
	
	@factory.post_generation
	def daysweek(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.daysweek.set(extracted)
	
	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.daysweek.set(create_daysweek())
		return obj


def create_time_group(**kwargs) -> models.TimeGroup:
	return TimeGroupFactory.create(**kwargs)

def create_time_group_without_dasyweek(**kwargs) -> models.TimeGroup:
	return TimeGroupBaseFactory.create(**kwargs)


class OfficeHourFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.OfficeHour

	interval_description = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	school = factory.SubFactory(SchoolFactory)
	time_group = factory.SubFactory(TimeGroupFactory)

	
def create_officehour(**kwargs) -> models.OfficeHour:
	return OfficeHourFactory.create(**kwargs)

def create_officehour_without_daysweek(**kwargs):
	return OfficeHourFactory.create(
		time_group = create_time_group_without_dasyweek(),
		**kwargs
	)

def bulk_create_officehour(size:int = 1, **kwargs) -> list[models.OfficeHour]:
	return OfficeHourFactory.create_batch(size = size, **kwargs)

def bulk_create_officehour_without_daysweek(size:int = 1, **kwargs) -> list[models.OfficeHour]:
	return OfficeHourFactory.create_batch(
		size = size,
		time_group = create_time_group_without_dasyweek(),
		**kwargs
	)

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


class NewsMediaFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.NewsMedia

	title = faker.name()
	photo = faker.image_url()

def create_news_media(**kwargs) -> list[models.NewsMedia]:
	return NewsMediaFactory.create_batch(size = kwargs.get("size", 1))


class NewsFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.News

	title = faker.text(max_nb_chars = 20)
	description = faker.paragraph()
	status = factory.fuzzy.FuzzyChoice(models.News.TypeStatus.values)
	school = factory.SubFactory(SchoolFactory)

	@factory.post_generation
	def media(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.media.set(extracted)


def create_news(**kwargs) -> models.News:
	return NewsFactory.create(**kwargs, media = create_news_media(size = 5))


def bulk_create_news(size: int = 1, **kwargs) -> list[models.News]:
	return NewsFactory.create_batch(size = size, **kwargs)


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