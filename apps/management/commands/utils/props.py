import datetime
from typing import TypeVar
from typing_extensions import Annotated

from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import InMemoryUploadedFile

from pydantic import BaseModel, AnyHttpUrl, ConfigDict

from apps.school import models


UploadedFile = TypeVar("UploadedFile", bound=InMemoryUploadedFile)
ListUploadedFile = TypeVar("ListUploadedFile", bound = list[UploadedFile])
DjangoDict = TypeVar("DjangoDict", bound=MultiValueDict)
TimeGroupModel = TypeVar("TimeGroupModel", bound=models.TimeGroup)

IsProfileURL = str
ProfileURL = Annotated[str, AnyHttpUrl]
ListProfileURL = Annotated[list[str], list[AnyHttpUrl]]

Profile = ProfileURL | ListProfileURL

class NewsParam(BaseModel):
	title: str 
	description: str | None = None
	status: str | None = None

class TimeGroupByIdParam(BaseModel):
	id: int

class TimeGroupParam(BaseModel):
	type: str
	daysweek: list[int]| None = None
	opening_time: datetime.time
	closing_time: datetime.time
	active: bool | None = models.TYPEGROUP_ACTIVE_DEFAULT
	overview: str | None = None


class OfficeHourParam(BaseModel):
	description: str
	time_group: TimeGroupParam | TimeGroupByIdParam


class CalendarParam(BaseModel):
	title: str
	description: str | None = None
	date: datetime.date


class CoordinateParam(BaseModel):
	title: str
	latitude: float
	longitude: float


class StaffParam(BaseModel):
	name: str
	occupation: str | None = None


class GradeValidateParam(BaseModel):
	level: int
	section: str
	stage_id: int
	

class GradeParam(BaseModel):
	name: str
	level: int
	section: str | None = None
	description: str | None = None 
	stage_id: int
	teachers: list[int] | None = None


class RepositoryParam(BaseModel):
	model_config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True)
	
	name_project: str
	description: str = None
	media: ListUploadedFile | None = None
