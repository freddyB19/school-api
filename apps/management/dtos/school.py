import datetime
from typing import TypeVar

from django.core.files.uploadedfile import InMemoryUploadedFile

from pydantic import BaseModel, ConfigDict

UploadedFile = TypeVar("UploadedFile", bound=InMemoryUploadedFile)
ListUploadedFile = TypeVar("ListUploadedFile", bound = list[UploadedFile])

class BaseDTO(BaseModel):
	model_config = ConfigDict(extra = "ignore", frozen = True, arbitrary_types_allowed = True)

	@property
	def data(self) -> dict:
		return self.model_dump(exclude_defaults = True)

class NewsCreateDTO(BaseDTO):
	title: str
	status: str | None = None
	description: str | None = None
	images: ListUploadedFile | None = None


class NewsUpdateImages(BaseDTO):
	images: ListUploadedFile


class TimeGroupDTO(BaseDTO):
	type: str
	daysweek: list[int] | None = None
	opening: datetime.time
	closing: datetime.time
	active: bool | None = None
	overview: str | None = None


class OfficeHourUpdateDTO(BaseDTO):
	interval_description: str | None = None
