from typing import TypeVar

from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import InMemoryUploadedFile

from pydantic import BaseModel, field_validator

from apps.school import models
from apps.utils.functions import validate_choice

from .errors_messages import NewsParamErrorsMessages


UploadedFile = TypeVar("UploadedFile", bound=InMemoryUploadedFile)
DjangoDict = TypeVar("DjangoDict", bound=MultiValueDict)

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