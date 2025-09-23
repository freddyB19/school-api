import datetime
from pydantic import BaseModel
from dataclasses import dataclass

@dataclass(frozen = True)
class TimeGroupDTO:
	type: str 
	daysweek: list[int]
	opening: datetime.time
	closing: datetime.time
	active: bool
	overview: str

	@property
	def data(self):
		return self.__getstate__()

@dataclass(frozen = True)
class OfficeHourDTO:
	interval_description: str

	@property
	def data(self):
		return self.__getstate__()

