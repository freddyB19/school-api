from apps.school import models

class NewsParamErrorsMessages:
	MAX_LEN = "El título de la noticia es muy largo"
	MIN_LEN = "El título de la noticia es muy corto"
	INVALID_STATUS = "Opción incorrecta para el estado de la noticia"


class SchoolErrorsMessages:
	DoesNotExist = "No existe información sobre esta escuela"


class TimeGroupErrorsMessages:
	MAX_LEN = models.ERROR_MESSAGE_MAX_LEN_TYPE
	DOES_NOT_EXIST = "No existe información sobre este grupo horario"
	MIN_LEN = models.ERROR_MESSAGE_MIN_LEN_TYPE
	INVALID_DAYSWEEK = f"El día de la semana elegido es invalido, debe ser un valor entre: {models.DaysNumber.values}"
	WRONG_TIME = models.OPENING_CLOSING_TIME


class OfficeHourErrorsMessages:
	MAX_LEN = models.ERROR_MESSAGE_MIN_LEN_INTERVAL_D
	MIN_LEN = models.ERROR_MESSAGE_MAX_LEN_INTERVAL_D
