from typing import TypeVar
from datetime import datetime

from rest_framework import serializers

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


from apps.school import models

from apps.utils.result_commands import ResponseError

from apps.school.apiv1 import serializers as school_serializer

from apps.management.commands import commands
from apps.management.dtos import school as school_dto

ERROR_FIELD = lambda field, type, symbol, value: f"El campo '{field}' es muy {type}, debe ser {symbol} a {value}" 

MIN_LENGTH_FIELDS = 10

class SchoolUpdateRequest(serializers.ModelSerializer):
	class Meta:
		model = models.School
		exclude = ["private", "logo"]

		read_only_fields = ["id", "subdomain"]

		extra_kwargs = {
			"name": {
				"max_length": models.MAX_LENGTH_SCHOOL_ADDRESS,
				"min_length": models.MIN_LENGTH_SCHOOL_ADDRESS,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "nombre", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_NAME
					),
					"min_length": ERROR_FIELD(
						field = "nombre", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_SCHOOL_NAME
					)
				}
			},
			"address": {
				"max_length": models.MAX_LENGTH_SCHOOL_ADDRESS,
				"min_length": models.MIN_LENGTH_SCHOOL_ADDRESS,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "dirección", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_ADDRESS
					),
					"min_length": ERROR_FIELD(
						field = "misión",
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_SCHOOL_ADDRESS
					)
				}
			},
			"mission": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "misión", 
						type = "corto",
						symbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
			"vision": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "visión", 
						type = "corto",
						symbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
			"history": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "historia", 
						type = "corto",
						symbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
		}


class SchoolUpdateLogoRequest(serializers.Serializer):
	logo = serializers.ImageField(max_length = 20)


MAX_LENGTH_IMAGE_NAME = 20

STATUS_INVALID_CHOICE = "La opción elegida es invalida"

class MSchoolNewsRequest(serializers.ModelSerializer):
	media = serializers.ListField(
		required = False,
		child = serializers.ImageField(max_length = MAX_LENGTH_IMAGE_NAME), 
	)
	
	class Meta:
		model = models.News
		fields = [
			"title",
			"media",
			"status",
			"description",
		]

		extra_kwargs = {
			"title": {
				"max_length": models.MAX_LENGTH_NEWS_TITLE,
				"min_length": models.MIN_LENGTH_NEWS_TITLE,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_NEWS_TITLE
					)
				}

			},
			"status": {
				"error_messages": {
					"invalid_choice": STATUS_INVALID_CHOICE
				}
			}
		}

	def create(self, validated_data) -> models.News:

		school_id = self.context.get("pk")
		
		validated = school_dto.NewsCreateDTO(
			images = validated_data.get("media"),
			**validated_data
		)

		command = commands.create_news(
			school_id = school_id,
			news = validated.data,
			images = validated.images
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors,
				).model_dump(exclude_defaults = True)
			)

		return command.query


class MSchoolNewsMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.NewsMedia
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class MSchoolNewsMediaField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo if image else None


class MSchoolNewsResponse(serializers.ModelSerializer):
	media = MSchoolNewsMediaSerializer(many = True)
	
	class Meta:
		model = models.News
		fields = "__all__"


class MSchoolNewsListResponse(serializers.ModelSerializer):
	media = MSchoolNewsMediaField(read_only = True)

	class Meta:
		model = models.News
		fields = ["id", "title", "created", "updated", "media", "status"]


class MSchoolNewsUpdateRequest(serializers.ModelSerializer):
	class Meta:
		model = models.News
		fields = ["id", "title", "status", "description"]
		read_only_fields = ["id"]

		extra_kwargs = {
			"title": {
				"max_length": models.MAX_LENGTH_NEWS_TITLE,
				"min_length": models.MIN_LENGTH_NEWS_TITLE,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_NEWS_TITLE
					)
				}

			},
			"status": {
				"error_messages": {
					"invalid_choice": STATUS_INVALID_CHOICE
				}
			}
		}


class MSchoolNewsUpdateImagesRequest(serializers.Serializer):
	media = serializers.ListField(
		child = serializers.ImageField(max_length = MAX_LENGTH_IMAGE_NAME)
	)

	def update(self, instance, validated_data) -> models.News:
		validated = school_dto.NewsUpdateImages(
			images = validated_data.get("media")
		)

		command = commands.update_news_media(images = validated.images)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True)
			)
		
		instance.media.add(*command.query)		

		return instance


DAYWEEK_INVALID_CHOICE = f"El día de la semana elegido es invalido, debe ser entre: {models.DaysNumber.values}"

MIN_VALUE_DAY = 1
MAX_VALUE_DAY = 5

"""
	Los días de la semana son calificados desde 1 hasta el 5
	[L = 1, M = 2, Mi = 3, J = 4, V = 5]

	Permitiendo así una validación más facil.
"""

INVALID_CHOICES_DAY = lambda daysweek: list(
	filter(
		lambda num: num < MIN_VALUE_DAY or num > MAX_VALUE_DAY, 
		daysweek
	)
)
class MSchoolTimeGroupRequest(serializers.ModelSerializer):
	daysweek = serializers.ListField(
		child = serializers.IntegerField(),
		required = False
	)

	class Meta:
		model = models.TimeGroup
		fields = "__all__"
		read_only_fields = ["id"]
		extra_kwargs = {
			"type": {
				"max_length": models.MAX_LENGTH_TYPEGROUP_TYPE,
				"min_length": models.MIN_LENGTH_TYPEGROUP_TYPE,
				"error_messages": {
					"max_length":ERROR_FIELD(
						field = "tipo", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_TYPEGROUP_TYPE
					),
					"min_length": ERROR_FIELD(
						field = "tipo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_TYPEGROUP_TYPE
					)
				}
			}
		}

	def validate_daysweek(self, value):
		is_invalid = INVALID_CHOICES_DAY(daysweek = value)

		if is_invalid:
			raise serializers.ValidationError(
				DAYWEEK_INVALID_CHOICE,
				code="invalid"
			)

		return value

	def validate(self, data):

		opening_time = data.get("opening_time")
		closing_time = data.get("closing_time")

		if not opening_time and not closing_time:
			return data

		time = [opening_time, closing_time]
		INVALID_TIME_SENT = None 
		ERROR_MESSAGE = "Debe enviar ámbos valores [opening_time, closing_time]"

		if INVALID_TIME_SENT in time:
			# Validamos si solo se ha enviado un solo valor
			# en relación con [opening_time, closing_time]
			
			raise serializers.ValidationError(
				ERROR_MESSAGE,
				code="invalid_request"
			)

		if closing_time <= opening_time:
			raise serializers.ValidationError(
				models.OPENING_CLOSING_TIME, 
				code = "invalid_time"
			)

		return data

SCHOOL_DOES_NOT_EXIST = "No existe una 'escuela' con ese id"
TIMEGROUP_DOES_NOT_EXIST = "No existe un 'grupo horario' con ese id"
INVALID_TIMEGROUP = "Debe definir un nuevo 'grupo horario' o seleccionar uno ya existente"

class MSchoolOfficeHourRequest(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupRequest(required = False)
	time_group_id = serializers.IntegerField(
		required = False,
		min_value = 1
	)
	description = serializers.CharField(
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "larga",
				symbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corta",
				symbol = "mayor o igual",
				value = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D
			)
		}
	)

	class Meta:
		model = models.OfficeHour
		fields = ["description", "time_group", 'time_group_id']

	def validate_time_group_id(self, value):
		school = commands.get_school_by_id(
			id = self.context.get("pk")
		).query

		if not school:
			raise serializers.ValidationError(
				SCHOOL_DOES_NOT_EXIST,
				code="does-not-exist"
			)
			
		if not school.officeHoursList.filter(time_group_id = value).exists():
			raise serializers.ValidationError(
				TIMEGROUP_DOES_NOT_EXIST,
				code="does-not-exist"
			)

		return value


	def validate(self, data):
		time_group = data.get("time_group")
		time_group_id = data.get("time_group_id")

		if not time_group and not time_group_id:
			raise serializers.ValidationError(
				INVALID_TIMEGROUP,
				code="required"
			)

		if time_group and time_group_id:
			raise serializers.ValidationError(
				INVALID_TIMEGROUP,
				code="invalid"
			)

		return data


	def create(self, validated_data):

		new_time_group = validated_data.get("time_group")
		time_group_id = validated_data.get("time_group_id")

		time_group = new_time_group or school_dto.TimeGroupByIdDTO(id = time_group_id)

		office_hour = school_dto.OffiHourCreateDTO(
			description = validated_data.get("description"),
			time_group = time_group
		).data

		command = commands.create_office_hour(
			school_id = self.context.get("pk"),
			office_hour = office_hour,
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True)
			)

		return command.query



OfficeHour = TypeVar("OfficeHour", bound = models.OfficeHour)

class MSchoolOfficeHourUpdateRequest(serializers.Serializer):
	description = serializers.CharField(
		required = True,
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "largo",
				symbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corto",
				symbol = "mayor o igual",
				value = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D
			)
		}
	)

	def update(self, instance: OfficeHour, validated_data: dict[str, str]) -> OfficeHour:
		validated = school_dto.OfficeHourUpdateDTO(
			interval_description = validated_data.get(
				"description", 
				instance.interval_description
			)
		).data
		
		instance.interval_description = validated.get("interval_description")
		
		return instance


class MSchoolTimeGroupResponse(serializers.ModelSerializer):
	daysweek = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name'
    )
	
	class Meta:
		model = models.TimeGroup
		fields = "__all__"


class MSchoolTimeGroupListResponse(MSchoolTimeGroupResponse):
	class Meta:
		model = models.TimeGroup
		exclude = ["overview"]

class MSchoolOfficeHourResponse(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupResponse(read_only = True)
	
	class Meta:
		model = models.OfficeHour
		fields = "__all__"


class MSchoolOfficeHourListResponse(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupListResponse(read_only = True)

	class Meta:
		model = models.OfficeHour
		fields = ["id", "interval_description", "time_group"]


class MSchoolCalendarListResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		fields = ["id", "title", "date"]


CALENDAR_ALREADY_EXISTS = "Ya existe un registro con el mismo título y fecha"

class MSchoolCalendarRequest(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		fields = ["title", "description", "date"]
		extra_kwargs = {
			"title": {
				"min_length": models.MIN_LENGTH_CALENDAR_TITLE,
				"max_length": models.MAX_LENGTH_CALENDAR_TITLE,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_CALENDAR_TITLE
					),
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_CALENDAR_TITLE
					),
				}
			}
		}

	def validate(self, data):
		title = data.get("title")
		date = data.get("date")
 
		calendar = commands.calendar_exist(
			school_id = self.context.get("pk"), 
			title = title, 
			date = date
		).query
		
		if calendar:
			raise serializers.ValidationError(
				CALENDAR_ALREADY_EXISTS,
				code="already_exists"
			)
			
		return data


	def create(self, validated_data):

		command  = commands.create_calendar(
			school_id = self.context.get("pk"),
			calendar = validated_data
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True),
				code = "invalid"
			)

		return command.query


class MSchoolCalendarResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		exclude = ["school"]


SOCIALMEDIA_ALREADY_EXISTS = "Esta enviado una red social que ya se encuentra registrada"
INVALID_SOCIALMEDIA = "Debes enviar un enlace de tu red social"
INVALID_REQUEST_SOCIALMEDIA = "Debes solo enviar solo una opción [profile | profiles], pero no ambos."

class MSchoolSocialMediaResquest(serializers.Serializer):
	profile = serializers.URLField(required = False)
	profiles = serializers.ListField(
		child = serializers.URLField(),
		required = False
	)

	def validate(self, data):

		profile = data.get("profile")
		profiles = data.get("profiles")

		if profile and profiles:
			raise serializers.ValidationError(
				INVALID_REQUEST_SOCIALMEDIA,
				code = "invalid"
			)

		if not profile and not profiles:
			raise serializers.ValidationError(
				INVALID_SOCIALMEDIA,
				code = "invalid"
			)

		social_network = profile or profiles
		
		social_network_exist = commands.social_media_exist(
			school_id = self.context.get("pk"),
			social_network = social_network
		).query

		if social_network_exist:
			raise serializers.ValidationError(
				SOCIALMEDIA_ALREADY_EXISTS,
				code = "already-exists"
			)
		
		return data

	def create(self, validated_data):
		profile = validated_data.get("profile")
		profiles = validated_data.get("profiles")

		social_network = profile or profiles

		command = commands.create_social_media(
			school_id = self.context.get("pk"),
			social_network = social_network
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True),
				code = "invalid"
			)

		return command.query


class MSchoolSocialMediaReponse(serializers.ModelSerializer):

	class Meta:
		model = models.SocialMedia
		fields = ["id", "profile"]

class MSchoolSocialMediaUpdateRequest(serializers.ModelSerializer):

	class Meta:
		model = models.SocialMedia
		fields = ["id", "profile"]
		read_only_fields = ["id"]