import datetime
from typing import TypeVar
from typing_extensions import Annotated

from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import InMemoryUploadedFile

from pydantic import (
	BaseModel, 
	AfterValidator,
	PlainValidator,
	field_validator, 
	model_validator,
)

from apps.school import models
from apps.utils.functions import validate_choice

from .errors_messages import (
	NewsParamErrorsMessages,
	TimeGroupErrorsMessages,
	OfficeHourErrorsMessages
)


UploadedFile = TypeVar("UploadedFile", bound=InMemoryUploadedFile)
ListUploadedFile = TypeVar("ListUploadedFile", bound = list[UploadedFile])
DjangoDict = TypeVar("DjangoDict", bound=MultiValueDict)
TimeGroupModel = TypeVar("TimeGroupModel", bound=models.TimeGroup)


VALIDATE_MAX_LEN = lambda value, max_len: value > max_len
VALIDATE_MIN_LEN = lambda value, min_len: value < min_len


class NewsParam(BaseModel):
	title: str 
	description: str | None = None
	status: str | None = None

	@field_validator('title', mode='after')
	@classmethod
	def length_title(cls, value):
		if VALIDATE_MAX_LEN(value = len(value), max_len = models.MAX_LENGTH_NEWS_TITLE):
			raise ValueError(NewsParamErrorsMessages.MAX_LEN)
		elif VALIDATE_MIN_LEN(value = len(value), min_len = models.MIN_LENGTH_NEWS_TITLE):
			raise ValueError(NewsParamErrorsMessages.MIN_LEN)
		return value

	@field_validator("status", mode= "after")
	@classmethod
	def choice_status(cls, value):
		if not validate_choice(choice = value, options = models.News.TypeStatus):
			raise ValueError(NewsParamErrorsMessages.INVALID_STATUS)
		return value



"""
	Los días de la semana son calificados desde 1 hasta el 5
	[L = 1, M = 2, Mi = 3, J = 4, V = 5]

	Permitiendo así una validación más facil.
"""

MIN_VALUE_DAY = 1
MAX_VALUE_DAY = 5

VALIDATE_CHOICES_DAY = lambda daysweek: list(
	filter(
		lambda num: num < MIN_VALUE_DAY or num > MAX_VALUE_DAY, 
		daysweek
	)
)
class TimeGroupByIdParam(BaseModel):
	id: int

class TimeGroupParam(BaseModel):
	type: str
	daysweek: list[int]| None = None
	opening_time: datetime.time
	closing_time: datetime.time
	active: bool | None = models.TYPEGROUP_ACTIVE_DEFAULT
	overview: str | None = None

	@field_validator("type", mode= "after")
	@classmethod
	def length_type(cls, value):
		if VALIDATE_MAX_LEN(value = len(value), max_len = models.MAX_LENGTH_TYPEGROUP_TYPE):
			raise ValueError(TimeGroupErrorsMessages.MAX_LEN)

		elif VALIDATE_MIN_LEN(value = len(value), min_len = models.MIN_LENGTH_TYPEGROUP_TYPE):
			raise ValueError(TimeGroupErrorsMessages.MIN_LEN)

		return value

	def _delete_duplicate(value) -> list[int]:
		return list(set(value))

	@field_validator("daysweek", mode= "after")
	@classmethod
	def choices_daysweek(cls, value):
		is_valid = VALIDATE_CHOICES_DAY(daysweek = cls._delete_duplicate(value))
		
		if is_valid:
			raise ValueError(TimeGroupErrorsMessages.INVALID_DAYSWEEK)

		return value


	@model_validator(mode = "after")
	def check_time(self):
		
		if self.closing_time <= self.opening_time:
			raise ValueError(TimeGroupErrorsMessages.WRONG_TIME)

		return self


def check_len_description(value: str) -> str:

	if VALIDATE_MAX_LEN(value = len(value), max_len = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D):
		raise ValueError(OfficeHourErrorsMessages.MAX_LEN)
	elif VALIDATE_MIN_LEN(value = len(value), min_len = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D):
		raise ValueError(OfficeHourErrorsMessages.MIN_LEN)
	
	return value

IntervalDescription = Annotated[str, AfterValidator(check_len_description)]


class OfficeHourParam(BaseModel):
	description: IntervalDescription
	time_group: TimeGroupParam | TimeGroupByIdParam
