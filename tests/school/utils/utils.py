from typing import TypeVar

import datetime, random

import factory, factory.fuzzy

from tests import faker

from apps.school import models


TimeSeries = TypeVar("TimeSeries", bound = list[tuple[datetime.datetime, float]])

class DefineTimelimits:

	@classmethod
	def _format_time(cls, hour):
		now = datetime.datetime.now()
		return datetime.datetime(now.year, now.month, now.day, hour)

	@classmethod
	def _define_time_series(cls, start_hour: int, end_hour: int) -> TimeSeries:
		if start_hour >= end_hour:
			raise TypeError("'start_hour' debe ser mayor a 'end_hour'")
		
		time_series = list(faker.time_series(
			start_date = cls._format_time(start_hour), 
			end_date = cls._format_time(end_hour)
		))
		
		return time_series

	@classmethod
	def _get_random_time(cls, time_series: TimeSeries) -> datetime.datetime:
		time = random.choice(time_series)
		return time[0].time()

	@classmethod
	def get(cls, start_hour:int, end_hour:int) -> datetime.datetime:
		time_series = cls._define_time_series(
			start_hour = start_hour, 
			end_hour = end_hour
		)
		return cls._get_random_time(time_series)



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

	name = factory.LazyAttribute(lambda x: faker.name())
	subdomain = factory.LazyAttributeSequence(lambda obj, num: f"{faker.domain_word()}-{num}") 
	logo = faker.image_url()
	address = faker.address()
	mission = faker.paragraph()
	vision = faker.paragraph()
	history = faker.paragraph()
	private = factory.fuzzy.FuzzyChoice((True, False))

def create_school(**kwargs) -> models.School:
	return SchoolFactory.create(**kwargs)


class ColorHexFormatFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.ColorHexFormat

	color = factory.LazyAttribute(lambda x: faker.hex_color())

def create_color_hex_format(**kwargs) -> models.ColorHexFormat:
	return ColorHexFormatFactory.create(**kwargs)

def bulk_create_color_hex_format(size: int = 1, **kwargs) -> list[models.ColorHexFormat]:
	return ColorHexFormatFactory.create_batch(size = size, **kwargs)


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


class CalendarFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Calendar

	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	date = factory.LazyAttribute(lambda x: faker.date_this_year())
	school = factory.SubFactory(SchoolFactory)


def create_calendar(**kwargs) -> models.Calendar:
	return CalendarFactory.create(**kwargs)

def bulk_create_calendar(size: int = 1, **kwargs) -> list[models.Calendar]:
	return CalendarFactory.create_batch(size = size, **kwargs)


class SocialMediaFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.SocialMedia

	profile = factory.LazyAttribute(lambda x: faker.url())
	school = factory.SubFactory(SchoolFactory)

def create_social_media(**kwargs) -> models.SocialMedia:
	return SocialMediaFactory.create(**kwargs)

def bulk_create_social_media(size:int = 1, **kwargs) -> models.SocialMedia:
	return SocialMediaFactory.create_batch(size = size, **kwargs)


class  CoordinateFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Coordinate

	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	latitude = factory.LazyAttribute(lambda x: faker.local_latlng(country_code = 'VE')[0])
	longitude = factory.LazyAttribute(lambda x: faker.local_latlng(country_code = 'VE')[1])
	school = factory.SubFactory(SchoolFactory)


def create_coordinate(**kwargs) -> models.Coordinate:
	return CoordinateFactory.create(**kwargs)

def bulk_create_coordinate(size:int = 1, **kwargs) -> list[models.Coordinate]:
	return CoordinateFactory.create_batch(size = size, **kwargs)


class SchoolStaffFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.SchoolStaff

	name = factory.LazyAttribute(lambda x: faker.name())
	school = factory.SubFactory(SchoolFactory)


def create_school_staff(**kwargs) -> models.SchoolStaff:
	return SchoolStaffFactory.create(**kwargs)

def bulk_create_school_staff(size:int = 1, **kwargs) -> list[models.SchoolStaff]:
	return SchoolStaffFactory.create_batch(size = size, **kwargs)


class EducationalStageFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.EducationalStage

	type = factory.fuzzy.FuzzyChoice(models.TypeEducationalStage)


class GradeFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Grade
	
	name = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 15))
	level = factory.LazyAttribute(lambda x: faker.random_int(min = 1, max = 7))
	section = factory.LazyAttribute(lambda x: "".join(faker.random_letters(length = 3)))
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)
	stage = factory.SubFactory(EducationalStageFactory)


	@factory.post_generation
	def teacher(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.teacher.set(extracted)

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.teacher.add(create_school_staff(
			occupation = models.OccupationStaff.teacher,
			school = obj.school
		))
		return obj

def create_grade(**kwargs) -> models.Grade:
	return GradeFactory.create(**kwargs)

def bulk_create_grade(size:int = 1, **kwargs) -> models.Grade:
	return GradeFactory.create_batch(size = size,**kwargs)



class SchoolMediaFileFactory(factory.django.DjangoModelFactory):
	class Meta:
		abstract = True
	
	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	file = factory.LazyAttribute(
		lambda x: f"{faker.url()}{faker.file_path(category = 'office')[1:]}"
	)

class SchoolMediaPhotoFactory(factory.django.DjangoModelFactory):
	class Meta:
		abstract = True

	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	photo = factory.LazyAttribute(lambda x: faker.image_url())


class RepositoryMediaFileFactory(SchoolMediaFileFactory):
	class Meta:
		model = models.RepositoryMediaFile


def bulk_create_media_respository(size:int = 1, **kwargs) -> list[models.RepositoryMediaFile]:
	return RepositoryMediaFileFactory.create_batch(size = size, **kwargs)


class RepositoryFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Repository

	name_project = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)


	@factory.post_generation
	def media(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.media.add(*(extracted))

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.media.set(bulk_create_media_respository(size = 3))
		return obj


def create_repository(**kwargs) -> models.Repository:
	return RepositoryFactory.create(**kwargs)

def bulk_create_repository(size:int = 1, **kwargs) -> list[models.Repository]:
	return RepositoryFactory.create_batch(size = size, **kwargs)


class InfraestructureMediaFactory(SchoolMediaPhotoFactory):
	class Meta:
		model = models.InfraestructureMedia

def bulk_create_infraestructure_media(size:int = 1, **kwargs) -> list[models.InfraestructureMedia]:
	return InfraestructureMediaFactory.create_batch(size = size, **kwargs)


class InfraestructureFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Infraestructure

	name = factory.LazyAttribute(lambda x: faker.name())
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)

	@factory.post_generation
	def media(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.media.add(*(extracted))

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.media.set(bulk_create_infraestructure_media(size = 5))
		return obj

def create_infraestructure(**kwargs) -> models.Infraestructure:
	return InfraestructureFactory.create(**kwargs)

def bulk_create_infraestructure(size:int = 1, **kwargs) -> list[models.Infraestructure]:
	return InfraestructureFactory.create_batch(size = size, **kwargs)


class DownloadFactory(SchoolMediaFileFactory):
	class Meta:
		model = models.Download

	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)

def create_download(**kwargs) -> models.Download:
	return DownloadFactory.create(**kwargs)

def bulk_create_download(size:int = 1, **kwargs) -> list[models.Download]:
	return DownloadFactory.create_batch(size = size, **kwargs)


class NewsMediaFactory(SchoolMediaPhotoFactory):
	class Meta:
		model = models.NewsMedia

def bulk_create_news_media(size:int = 1,**kwargs) -> list[models.NewsMedia]:
	return NewsMediaFactory.create_batch(size = size, **kwargs)


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

		self.media.add(*(extracted))

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.media.set(bulk_create_news_media(size = 3))
		return obj

def create_news(**kwargs) -> models.News:
	return NewsFactory.create(**kwargs)

def bulk_create_news(size: int = 1, **kwargs) -> list[models.News]:
	return NewsFactory.create_batch(size = size, **kwargs)


class CulturaEventMediaFactory(SchoolMediaPhotoFactory):
	class Meta:
		model = models.CulturalEventMedia


def bulk_create_cultura_event_media(size: int = 1, **kwargs) -> list[models.CulturalEventMedia]:
	return CulturaEventMediaFactory.create_batch(size = size, **kwargs)


class CulturaEventFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.CulturalEvent
		django_get_or_create = ('title', )

	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	date = factory.LazyAttribute(lambda x: faker.date_this_year())
	school = factory.SubFactory(SchoolFactory)

	@factory.post_generation
	def media(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.media.add(*(extracted))

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.media.set(bulk_create_cultura_event_media(size = 3))
		return obj


def create_cultura_event(**kwargs) -> models.CulturalEvent:
	return CulturaEventFactory.create(**kwargs)

def bulk_create_cultura_event(size:int = 1, **kwargs) -> list[models.CulturalEvent]:
	return CulturaEventFactory.create_batch(size = size, **kwargs)


class PaymentInfoFactory(SchoolMediaPhotoFactory):
	class Meta:
		model = models.PaymentInfo

	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)

def create_payment_info(**kwargs) -> models.PaymentInfo:
	return PaymentInfoFactory.create(**kwargs)

def bulk_create_payment_info(size:int = 1, **kwargs) -> list[models.PaymentInfo]:
	return PaymentInfoFactory.create_batch(size = size, **kwargs)


class PaymentReportFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.PaymentReport

	fullname_student = factory.LazyAttribute(lambda x: faker.name())
	payment_detail = factory.LazyAttribute(lambda x: faker.url())
	grade = factory.SubFactory(GradeFactory)
	school = factory.SubFactory(SchoolFactory)


def create_payment_report(**kwargs) -> models.PaymentReport:
	return PaymentReportFactory.create(**kwargs)

def bulk_create_payment_report(size:int = 1, **kwargs) -> models.PaymentReport:
	return PaymentReportFactory.create(size = size, **kwargs)


class ConactInfoFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.ContactInfo

	email = factory.LazyAttribute(lambda x: faker.email())
	phone = factory.LazyAttribute(lambda x: f"{faker.random_number(digits = 11, fix_len = True)}")
	school = factory.SubFactory(SchoolFactory)


def create_contac_info(**kwargs) -> models.ContactInfo:
	return ConactInfoFactory.create(**kwargs)

def bulk_create_contac_info(size:int = 1, **kwargs) -> list[models.ContactInfo]:
	return ConactInfoFactory.create_batch(size = size, **kwargs)


class ExtraActivityScheduleFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.ExtraActivitySchedule

	type = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	opening_time = factory.LazyFunction(lambda: 
		DefineTimelimits.get(start_hour = 6, end_hour = 11)
	)
	closing_time = factory.LazyFunction(lambda: 
		DefineTimelimits.get(start_hour = 13, end_hour = 18)
	)
	active = factory.fuzzy.FuzzyChoice((True, False))

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

def create_extra_activity_schedule(**kwargs) -> models.ExtraActivitySchedule:
	return ExtraActivityScheduleFactory.create(**kwargs)

def bulk_create_extra_activity_schedule(size:int = 1, **kwargs) -> list[models.ExtraActivitySchedule]:
	return ExtraActivityScheduleFactory.create_batch(size = size, **kwargs)


class ExtraActivityFileFactory(SchoolMediaFileFactory):
	class Meta:
		model = models.ExtraActivityFile

def bulk_create_extra_activity_file(size: int = 1, **kwargs):
	return ExtraActivityFileFactory.create_batch(size = size, **kwargs)


class ExtraActivityPhotoFactory(SchoolMediaPhotoFactory):
	class Meta:
		model = models.ExtraActivityPhoto

def bulk_create_extra_activity_photo(size: int = 1, **kwargs) -> list[models.ExtraActivityPhoto]:
	return ExtraActivityPhotoFactory.create_batch(size = size, **kwargs)


class ExtraActivityFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.ExtraActivity

	title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars = 20))
	description = factory.LazyAttribute(lambda x: faker.paragraph())
	school = factory.SubFactory(SchoolFactory)

	@factory.post_generation
	def schedules(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.schedules.set(extracted)

	@factory.post_generation
	def files(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.files.set(extracted)

	@factory.post_generation
	def photos(self, create, extracted, **kwargs):
		if not create or not extracted:
			return

		self.photos.set(extracted)

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		obj = model_class(*args, **kwargs)
		obj.save()
		obj.schedules.set(bulk_create_extra_activity_schedule(size = 4))
		obj.files.set(bulk_create_extra_activity_file(size = 5))
		obj.photos.set(bulk_create_extra_activity_photo(size = 5))

		return obj


def create_extra_activity(**kwargs) -> models.ExtraActivity:
	return ExtraActivityFactory.create(**kwargs)

def bulk_create_extra_activity(size:int = 1, **kwargs) -> list[models.ExtraActivity]:
	return ExtraActivityFactory.create_batch(size = size, **kwargs)