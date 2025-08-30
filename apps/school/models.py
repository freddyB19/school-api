from django.db import models
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator



MIN_LENGTH_SCHOOLMEDIA_TITLE = 5
MAX_LENGTH_SCHOOLMEDIA_TITLE = 100

class SchoolPhoto(models.Model):
	title = models.CharField(
		max_length = MAX_LENGTH_SCHOOLMEDIA_TITLE, 
		blank = True, 
		null = True,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_SCHOOLMEDIA_TITLE, message = "El titulo de la foto es muy corto")
		]
	)
	photo = models.URLField()

	class Meta:
		abstract = True



class SchoolFile(models.Model):
	title = models.CharField(
		max_length=MAX_LENGTH_SCHOOLMEDIA_TITLE,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_SCHOOLMEDIA_TITLE, message = "El titulo del archivo es muy corto")
		]
	)
	file = models.URLField()

	class Meta:
		abstract = True



MIN_LENGTH_SCHOOL_NAME = 5
MAX_LENGTH_SCHOOL_NAME = 50
MIN_LENGTH_SCHOOL_ADDRESS = 10
MAX_LENGTH_SCHOOL_ADDRESS = 100

class School(models.Model):
	name = models.CharField(
		max_length=MAX_LENGTH_SCHOOL_NAME, 
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_SCHOOL_NAME, message = "El nombre de la escuela es muy corto")
		]
	)
	subdomain = models.SlugField(unique = True)
	logo = models.URLField(blank = True, null = True)
	address = models.CharField(
		max_length=MAX_LENGTH_SCHOOL_ADDRESS,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_SCHOOL_ADDRESS, message = "La información de la dirección es muy corta")
		]
	)
	mission = models.TextField(blank = True, null = True)
	vision = models.TextField(blank = True, null = True) 
	history = models.TextField(blank = True, null = True)
	private = models.BooleanField(default = True)

	class Meta:
		verbose_name = "Escuela"
		verbose_name_plural = "Escuelas"
		db_table = "school"
		indexes = [
			models.Index(fields = ["subdomain"], name="subdomain_school_idx")
		]


	def __str__(self):
		return self.name

	def __repr__(self):
		return f"School(id = {self.id}, name = {self.name})"



class OccupationStaff(models.TextChoices):
	teacher = "profesor"
	administrative = "administrativo"

MIN_LENGTH_SCHOOSTAF_NAME = 5
MAX_LENGTH_SCHOOSTAF_NAME = 50
MAX_LENGTH_SCHOOSTAF_OCCUPATION = 15

class SchoolStaff(models.Model):
	name = models.CharField(
		max_length = MAX_LENGTH_SCHOOSTAF_NAME,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_SCHOOSTAF_NAME, message = "El nombre es muy corto")
		]
	)
	occupation = models.CharField(
        choices = OccupationStaff,
        default = OccupationStaff.administrative,
        max_length = MAX_LENGTH_SCHOOSTAF_OCCUPATION
    )
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="staffList",
		blank=True,
		null=True
    )
    
	class Meta:
		verbose_name = "Personal"
		verbose_name_plural = "Lista del personal"
		db_table = "school_staff"


	def __str__(self):
		return self.name

	def __repr__(self):
		return f"SchoolStaff(id = {self.id}, name = {self.name}, occupation = {self.occupation})"

# Hay que implementar un campo que nos ayude con la ordenación
# Ej: (Podemos aprovechar el TypeGrade) y asignar un numero al tipo de grado
# preescolar - 0
# básica - 1
# secundaria - 2
# ...

class TypeGradeByNumber(models.IntegerChoices):
	preschool = 0
	primary = 1
	high = 2

class TypeGrade(models.TextChoices):
	preschool = "preescolar"
	primary = "básica"
	high = "secundaria"

MIN_LENGTH_GRADE_NAME = 5
MAX_LENGTH_GRADE_NAME = 50
MAX_LENGTH_GRADE_TYPE = 11
MAX_LENGTH_GRADE_SECTION = 3
MIN_LENGTH_GRADE_SECTION = 1

class Grade(models.Model):
	
	name = models.CharField(
		max_length=MAX_LENGTH_GRADE_NAME,
		validators = [
			MinLengthValidator(
				limit_value = MIN_LENGTH_GRADE_NAME, 
				message = "El nombre es muy corto"
			)
		]
	)
	description = models.TextField(blank = True, null = True)
	type = models.CharField(
		choices = TypeGrade, 
		default = TypeGrade.primary, 
		max_length = MAX_LENGTH_GRADE_TYPE
	)
	type_number = models.IntegerField(choices = TypeGradeByNumber, default = TypeGradeByNumber.preschool)
	section = models.CharField(
		max_length = MAX_LENGTH_GRADE_SECTION, 
		blank = True, 
		null = True,
		validators = [
			MinLengthValidator(
				limit_value = MIN_LENGTH_GRADE_SECTION, 
				message = "El nombre es muy corto"
			)
		]
	)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="gradesList",
		blank=True,
		null=True
	)
	teacher = models.ManyToManyField(
		SchoolStaff,
		limit_choices_to = {"occupation": OccupationStaff.teacher},
		related_name="teacherList",
    )

	class Meta:
		verbose_name = "Grado"
		verbose_name_plural = "Grados de la escuela"
		db_table = "grade"

	def save(self, **kwargs):
		type_grade = {grade.value: str(grade.name) for grade in TypeGrade}
		which_grade = type_grade[self.type]

		self.type_number = TypeGradeByNumber[which_grade].value
		
		super().save(**kwargs)

	def __str__(self):
		return f"{self.name} - {self.section}"


	def __repr__(self):
		return f"Grade(id = {self.id}, name = {self.name}, type = {self.type}, school = {self.school.name})"



class InfraestructureMedia(SchoolPhoto):
	class Meta:
		verbose_name = "Foto de la infraestructura"
		verbose_name_plural = "Fotos de las infraestructuras"

	def __str__(self):
		return self.title if self.title else f"Archivo de imagen"

	def __repr__(self):
		return f"InfraestructureMedia(id = {self.id}, title = {self.title}, photo = {self.photo})"



MIN_LENGTH_INFRA_NAME = 5
MAX_LENGTH_INFRA_NAME = 100

class Infraestructure(models.Model):
	name = models.CharField(
		max_length = MAX_LENGTH_INFRA_NAME,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_INFRA_NAME, message = "El nombre es muy corto")
		]
	)
	description = models.TextField(blank = True, null = True)
	media = models.ManyToManyField(InfraestructureMedia)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="infraestructuresList",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Infraestructura"
		verbose_name_plural = "Infraestructuras"
		db_table = "infraestructure"
		indexes = [
			models.Index(fields=["school"], name="infraestructure_school_idx"),
		]

	def __str__(self):
		return self.name


	def __repr__(self):
		return f"Infraestructure(id = {self.id}, name = {self.name})"


	def get_absolute_url(self):
		return reverse(
			"school:infraestructure-detail", 
			kwargs = {"pk": self.id}
		)



MAX_LENGTH_CONTACTINFO_PHONE = 11

class ContactInfo(models.Model):
	email = models.EmailField(blank = True, null = True)
	phone = models.CharField(
		max_length = MAX_LENGTH_CONTACTINFO_PHONE,
		blank = True, 
		null = True,
		validators = [
			MinLengthValidator(
				limit_value = MAX_LENGTH_CONTACTINFO_PHONE, 
				message = "El número de telefono ingresado es incorrecto (es muy corto)"
			),
			MaxLengthValidator(
				limit_value = MAX_LENGTH_CONTACTINFO_PHONE,
				message = "El número de telefono ingresado es incorrecto (es muy largo)"
			)
		]
	)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="contactsList",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Información de contacto"
		verbose_name_plural = "Informaciones sobre contactos"
		db_table = "contact_info"

	def __str__(self):
		return f"{self.email} / {self.phone}"

	def __repr__(self):
		return f"ContactInfo(id = {self.id}, email = {self.email}, phone = {self.phone})"



class DaysName(models.TextChoices):
	monday = "Lunes"
	tuesday = "Martes"
	wednesday = "Miércoles"
	thursday = "Jueves"
	friday = "Viernes"

class DaysNumber(models.IntegerChoices):
	monday = 1
	tuesday = 2
	wednesday = 3
	thursday = 4
	friday = 5

MAX_LENGTH_DAYSWEEK_NAME = 10

class DaysWeek(models.Model):

	day = models.IntegerField(
		choices = DaysNumber, 
		default = DaysNumber.monday, 
		unique = True
	)
	name = models.CharField(
		max_length = MAX_LENGTH_DAYSWEEK_NAME, 
		editable = False, 
		default = DaysName.monday, 
		unique = True
	)

	class Meta:
		verbose_name = "Día de la Semana"
		verbose_name_plural = "Días de la Semana"
		ordering = ['day']
		db_table = "days_week"

	def save(self, **kwargs):
		days = {day.value: str(day.name) for day in DaysNumber}
		which_day = days[self.day]

		self.name = DaysName[which_day].value
		super().save(**kwargs)

	def __str__(self):
		return f"{self.day} - {self.name}"

	def __repr__(self):
		return f"DaysWeek(id = {self.id}, day = {self.day}, name = {self.name})"



MAX_LENGTH_TYPEGROUP_TYPE = 50

class TimeGroup(models.Model):
	# Sirve para indicar: Ej - (Turno Mañana, Turno Tarde, ...)
	type = models.CharField(max_length = MAX_LENGTH_TYPEGROUP_TYPE)
	daysweek = models.ManyToManyField(DaysWeek)
	opening_time = models.TimeField()
	closing_time = models.TimeField()
	active = models.BooleanField(default = True)
	overview = models.TextField(
		blank = True,
		null = True
	)

	class Meta:
		verbose_name = "Grupo de Horario"
		verbose_name_plural = "Grupos de Horarios"
		db_table = "time_group"

	def validate_opening_closing_time(self):
		if self.closing_time <= self.opening_time:
			raise ValidationError('La hora de cierre debe ser posterior a la hora de apertura', params = {'closing_time': self.closing_time})

	def __str__(self):

		return f"{self.type} : en un horario desde {self.opening_time.strftime('%H:%M')} hasta {self.closing_time.strftime('%H:%M')}"

	def __repr__(self):
		return f"TimeGroup(id = {self.id}, type = {self.type}, active = {self.active}, opening_time = {self.opening_time.strftime('%H:%M')}, closing_time = {self.closing_time.strftime('%H:%M')})"



MIN_LENGTH_OFFICEHOUR_INTERVAL_DESCRIPTION = 4
MAX_LENGTH_OFFICEHOUR_INTERVAL_DESCRIPTION = 100

class OfficeHour(models.Model):
	# Para indicar Descripción específica del intervalo (ej: Atención al cliente, Consultas)
	interval_description = models.CharField(
		max_length = MAX_LENGTH_OFFICEHOUR_INTERVAL_DESCRIPTION,
		validators = [
			MinLengthValidator(
				limit_value = MIN_LENGTH_OFFICEHOUR_INTERVAL_DESCRIPTION, 
				message = "La descripción sobre el horario de oficina, es muy corta"
			)
		]
	)
	time_group = models.ForeignKey(
		TimeGroup,
		on_delete=models.CASCADE,
		related_name="intervalsList",
		blank=True,
		null=True
	)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="officeHoursList",
		blank=True,
		null=True
	)
	
	class Meta:
		verbose_name = "Horario de oficina"
		verbose_name_plural = "Horarios de oficina"
		db_table = "office_hour"


	def __str__(self):
		return f"{self.interval_description} ({self.time_group.type})"

	def __repr__(self):
		return f"OfficeHour(id = {self.id}, time_group = {self.time_group.type})"


class SocialMedia(models.Model):
	profile = models.URLField()
	school = models.ForeignKey(
 		School, 
 		on_delete=models.CASCADE,
 		related_name="socialMediasList",
 		blank=True,
 		null=True
	)

	class Meta:
		verbose_name = "Red social"
		verbose_name_plural = "Redes sociales"
		db_table = "social_media"

	def __str__(self):
		return f"{self.profile} - [{self.school.name}]"

	def __repr__(self):
		return f"SocialMedia(id = {self.id}, profile = {self.profile})"


class CulturalEventMedia(SchoolPhoto):

	class Meta:
		verbose_name = "Foto de evento cultural"
		verbose_name_plural = "Fotos de eventos culturales"

	def __str__(self):
		return self.title if self.title else "Archivo de imagen"

	def __repr__(self):
		return f"CulturalEventMedia(id = {self.id}, title = {self.title}, photo = {self.photo})"

class CulturalEvent(models.Model):
	title = models.CharField(
		max_length=50,
		validators = [
			MinLengthValidator(limit_value = 5, message = "El titulo es muy corto")
		]
	)
	description = models.TextField(blank = True, null = True)
	date = models.DateField()
	media = models.ManyToManyField(CulturalEventMedia)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="culturalEventsList",
		blank=True,
		null=True
	)

	class Meta:
		unique_together = ["title", "school"]
		ordering = ["-date"]
		verbose_name = "Evento cultural"
		verbose_name_plural = "Eventos culturales"
		db_table = "cultural_event"
		indexes = [
			models.Index(fields = ["school"], name = "culturalevent_school_idx"),
			models.Index(fields = ["date"], name = "culturalevent_date_idx")

		]

	def __str__(self):
		return f"{self.title}"

	def __repr__(self):
		return f"CulturalEvent(id = {self.id}, title = {self.title}, date = {self.date})"


class Calendar(models.Model):
	title = models.CharField(
		max_length=50,
		validators = [
			MinLengthValidator(limit_value = 5, message = "El titulo es muy corto")
		]
	)
	description = models.TextField(blank = True, null = True)
	date = models.DateField()
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="calendarsList",
		blank=True,
		null=True
	)
	
	class Meta:
		verbose_name = "Calendario"
		verbose_name_plural = "Fechas del calendario"
		db_table = "calendar"
		ordering = ["-date"]
		indexes = [
			models.Index(fields = ["school"], name = "calendar_school_idx"),
			models.Index(fields = ["date"], name = "calendar_date_idx")
		]

	def __str__(self):
		return self.title

	def __repr__(self):
		return f"Calendar(id = {self.id}, title = {self.title}, date = {self.date})"


class NotificationCDCE(models.Model):
	title = models.CharField(
		max_length=70,
		validators = [
			MinLengthValidator(limit_value = 5, message = "El titulo es muy corto")
		]
	)
	description = models.TextField(blank = True, null = True)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="notificationsList",
		blank=True,
		null=True
	)

	class Meta:
		ordering = ["-created"]
		db_table = "notification_cdce"
		verbose_name = "Notificación CDCE"
		verbose_name_plural = "Notificaciones CDCE"
		indexes = [
			models.Index(fields = ["school"], name = "notification_school_idx"),
			models.Index(fields = ["created"], name = "notification_created_idx")
		]

	def __str__(self):
		return f"{self.title}"

	def __repr__(self):
		return f"NotificationCDCE(id = {self.id}, title = {self.title})"

class NewsMedia(SchoolPhoto):

	class Meta:
		verbose_name = "Foto de la noticia"
		verbose_name_plural = "Fotos de las noticias"
		db_table = "new_media"

	def __str__(self):
		return self.title if self.title else "Archivo de imagen"

	def __repr__(self):
		return f"NewsMedia(id = {self.id}, title = {self.title}, photo = {self.photo})"


MAX_LENGTH_NEWS_TITLE = 70
MIN_LENGTH_NEWS_TITLE = 5
MAX_LENGTH_NEWS_STATUS = 10

class News(models.Model):
	class TypeStatus(models.TextChoices):
		pending = "pendiente"
		published = "publicado"

	title = models.CharField(
		max_length=MAX_LENGTH_NEWS_TITLE,
		validators = [
			MinLengthValidator(limit_value = MIN_LENGTH_NEWS_TITLE, message = "El titulo es muy corto")
		]
	)
	description = models.TextField(blank = True, null = True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now = True)
	status = models.CharField(
		choices = TypeStatus, 
		default = TypeStatus.published,
		max_length = MAX_LENGTH_NEWS_STATUS
	)
	media = models.ManyToManyField(NewsMedia)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="newsList",
		blank=True,
		null=True
    )

	class Meta:
		verbose_name = "Noticia"
		verbose_name_plural = "Noticias"
		db_table = "news"
		ordering = ["-created", "-updated"]
		indexes = [
			models.Index(fields = ["school"], name = "news_school_idx"),
			models.Index(fields = ["created"], name = "news_created_idx")
		]


	def __str__(self):
		return f"{self.title}"

	def __repr__(self):
		return f"NotificationCDCE(id = {self.id}, title = {self.title})"


class PaymentInfo(SchoolPhoto):
	description = models.TextField(blank = True, null = True)
	
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="paymentInfoList",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Información de pago"
		verbose_name_plural = "Información de pagos"
		ordering = ["-id"]
		db_table = "payment_info"

	def __str__(self):
		return f"Escuela[{self.school.name}] - Información de pago: {self.photo}"

	def __repr__(self):
		return f"PaymentInfo(id = {self.id}, photo = {self.photo})"


class PaymentReport(models.Model):
	fullname_student = models.CharField(
		max_length=100, 
		validators = [
			MinLengthValidator(limit_value = 5, message = "El nombre del estudiante es muy corto, ingrese el nombre completo")
		]
	)
	payment_detail = models.URLField()
	created = models.DateTimeField(auto_now_add=True)
	grade = models.ForeignKey(
		Grade,
		on_delete=models.CASCADE,
		related_name="gradesList",
		blank=True,
		null=True
	)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="paymentReportsList",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Reporte de pago"
		verbose_name_plural = "Reportes de pagos"
		ordering = ["-created"]
		db_table = "payment_report"
		indexes = [
			models.Index(fields = ["school"], name = "payment_report_school_idx"),
			models.Index(fields = ["created"], name = "payment_report_created_idx")
		]


	def __str__(self):
		return f"Escuela[{self.school.name}] - Reporte de pago: {self.payment_detail}"

	def __repr__(self):
		return f"PaymentReport(id = {self.id}, name_student = {self.name_student}, payment_detail = {self.payment_detail}, grade = {self.grade.name} - {self.grade.section}, school = {self.school.name})"


class Coordinate(models.Model):
	title = models.CharField(
		max_length=100,
		validators = [
			MinLengthValidator(limit_value = 4, message = "El titulo es muy corto")
		]
	)
	latitude = models.DecimalField(max_digits=8, decimal_places=5)
	longitude = models.DecimalField(max_digits=8, decimal_places=5)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="coordinatesList",
		blank=True,
		null=True
	)

	class Meta:
		unique_together = ['title', 'school']
		verbose_name = "Coordenada"
		verbose_name_plural = "Coordenadas"
		db_table = "coordinate"


	def __str__(self):
		return f"{self.title} : ({self.latitude}, {self.longitude})"

	def __repr__(self):
		return f"Coordinate(id = {self.id}, title = {self.title}, latitude = {self.latitude}, longitude = {self.longitude}, school = {self.school.name})"


def validate_hex_format(value):
	if not value.startswith("#"):
		raise ValidationError("El formato valido para los colores es en Hexadecimal", params = {"color": value})


class ColorHexFormat(models.Model):
	color = models.CharField(
		max_length = 8, 
		validators = [validate_hex_format]
	)

	class Meta:
		verbose_name = "Color en formato hexadecimal"
		verbose_name_plural = "Colores en formato hexadecimal"
		db_table = "color_hex_format"

	def __str__(self):
		return f"Color: {self.color}"

	def __repr__(self):
		return f"Color(id = {self.id}, color = {self.color})"


class SettingFormat(models.Model):
	colors = models.ManyToManyField(ColorHexFormat)
	school = models.OneToOneField(
		School,
		on_delete=models.CASCADE,
		related_name="setting",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Configuración"
		verbose_name_plural = "Configuraciones"
		db_table = "setting_format"
		

	def __str__(self):
		return f"Configuración de escuela: {self.school.name}"

	def __repr__(self):
		colors = ", ".join([color.color for color in self.colors.all()])
		return f"SettingFormat(id = {self.id}, colors = {colors}, school = {self.school.name})"


class Download(SchoolFile):
	description = models.TextField(blank = True, null = True)

	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="downloadsList",
		blank=True,
		null=True
	)

	class Meta:
		unique_together = ['title', 'school']
		verbose_name = "Descarga"
		verbose_name_plural = "Descargas"
		db_table = "download"
		indexes = [
			models.Index(fields = ["title"], name = "download_title_idx"),
			models.Index(fields = ["school"], name = "download_school_idx")
		]


	def __str__(self):
		return f"Archivo: {self.title}"

	def __repr__(self):
		return f"Download(id = {self.id}, title = {self.title}, file = {self.file}, school = {self.school.name})"


class RepositoryMediaFile(SchoolFile):

	class Meta:
		verbose_name = "Archivo multimedia del repositorio"
		verbose_name_plural = "Archivos multimedia de los repositorios"
		db_table = "repository_media_file"

	def __str__(self):
		return self.title if self.title else "Archivo multimedia"

	def __repr__(self):
		return f"RepositoryMediaFile(id = {self.id}, title = {self.title}, file = {self.file})"


class Repository(models.Model):
	name_project = models.CharField(
		max_length = 100,
		validators = [
			MinLengthValidator(
				limit_value = 4, 
				message = "El titulo del proyecto es muy corto"
			)
		]
	)
	description = models.TextField(
		blank = True,
		null = True,
	)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	media = models.ManyToManyField(RepositoryMediaFile)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="repositoriesList",
		blank=True,
		null=True
	)

	class Meta:
		unique_together = ['name_project', 'school']
		verbose_name = "Repositorio"
		verbose_name_plural = "Repositorios"
		db_table = "repository"
		ordering = ["-created", "-updated"]
		indexes = [
			models.Index(fields = ["name_project"], name = "repository_name_project_idx"),
			models.Index(fields = ["created"], name = "repository_created_idx"),
			models.Index(fields = ["school"], name = "repository_school_idx")
		]


	def __str__(self):
		return f"Escuela[{self.school.name}], Proyecto: {self.name_project}"

	def __repr__(self):
		return f"Repository(id = {self.id}, name_project = {self.name_project}, school = {self.school.name})"


class ExtraActivitiePhoto(SchoolPhoto):
	class Meta:
		verbose_name = "Foto de actividad extracurricular"
		verbose_name_plural = "Fotos de actividades extracurriculares"
		db_table = "extra_activitie_photo"

	def __str__(self):
		return self.title if self.title else f"Archivo de imagen"

	def __repr__(self):
		return f"ExtraActivitiesMediaPhotos(id = {self.id}, title = {self.title}, photo = {self.photo})"


class ExtraActivitieFile(SchoolFile):
	class Meta:
		verbose_name = "Archivo de actividad extracurricular"
		verbose_name_plural = "Archivos de actividades extracurriculares"
		db_table = "extra_activitie_file"


	def __str__(self):
		return self.title if self.title else f"Archivo de imagen"

	def __repr__(self):
		return f"ExtraActivitiesMediaFiles(id = {self.id}, title = {self.title}, file = {self.file})"


class ExtraActivitieSchedule(models.Model):
	type = models.CharField(max_length = 50)
	daysweek = models.ManyToManyField(DaysWeek)
	opening_time = models.TimeField(blank = True, null = True)
	closing_time = models.TimeField(blank = True, null = True)
	active = models.BooleanField(default = True)

	class Meta:
		verbose_name = "Horario de actividade extracurricular"
		verbose_name_plural = "Horarios de actividades extracurriculares"
		db_table = "extra_activitie_schedule"

	def validate_opening_closing_time(self):
		if self.closing_time <= self.opening_time:
			raise ValidationError('La hora de cierre debe ser posterior a la hora de apertura', params = {'closing_time': self.closing_time})

	def __str__(self):
		return f"[{self.type}] : en un horario desde {self.opening_time.strftime('%H:%M')} hasta {self.closing_time.strftime('%H:%M')}"

	def __repr__(self):
		return f"TimeGroup(id = {self.id}, type = {self.type}, active = {self.active}, opening_time = {self.opening_time.strftime('%H:%M')}, closing_time = {self.closing_time.strftime('%H:%M')})"


class ExtraActivitie(models.Model):
	title = models.CharField(
		max_length = 100,
		validators = [
			MinLengthValidator(limit_value = 5, message = "El titulo es muy corto")
		]
	)
	description = models.TextField(null = True, blank = True)
	files = models.ManyToManyField(ExtraActivitieFile)
	photos = models.ManyToManyField(ExtraActivitiePhoto)
	schedules = models.ManyToManyField(ExtraActivitieSchedule)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	school = models.ForeignKey(
		School, 
		on_delete=models.CASCADE,
		related_name="extraActivitiesList",
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = "Actividad extracurricular"
		verbose_name_plural = "Actividades extracurriculares"
		db_table = "extra_activitie"
		ordering = ["-created", "-updated"]
		indexes = [
			models.Index(fields = ["school"], name = "extra_activitie_school_idx"),
			models.Index(fields = ["created"], name = "extra_activitie_created_idx")
		]

	def __str__(self):
		return self.title if self.title else f"Actividad extracurricular de la escuela: [{self.school.name}]"

	def __repr__(self):
		return f"ExtraActivitie(id = {self.id}, title = {self.title}, school = {self.school.name})"