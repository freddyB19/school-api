from django.contrib import admin

from . import models


class SchoolAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"name",
		"subdomain"
	]

	list_filter = ["name", "private"]


class SchoolStaffAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"occupation",
		"school__name"
	]

	list_filter = ["occupation"]


class GradeAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"name",
		"type",
		"section",
		"school__name",
	]
	
	list_filter = ["school"]


class SocialMediaAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"profile",
		"school__name",
	]

	list_filter = ["school"]


class InfraestructureAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"name",
		"school__name",
	]

	list_filter = ["school"]

class ExtrarActivitiesAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"title",
		"school__name"
	]

	list_filter = ["school"]


admin.site.register(models.School, SchoolAdmin)
admin.site.register(models.SchoolStaff, SchoolStaffAdmin)
admin.site.register(models.Grade, GradeAdmin)
admin.site.register(models.Infraestructure, InfraestructureAdmin)
admin.site.register(models.InfraestructureMedia)
admin.site.register(models.ContactInfo)
admin.site.register(models.DaysWeek)
admin.site.register(models.TimeGroup)
admin.site.register(models.OfficeHour)
admin.site.register(models.SocialMedia, SocialMediaAdmin)
admin.site.register(models.CulturalEvent)
admin.site.register(models.CulturalEventMedia)
admin.site.register(models.Calendar)
admin.site.register(models.NotificationCDCE)
admin.site.register(models.NewMedia)
admin.site.register(models.News)
admin.site.register(models.PaymentInfo)
admin.site.register(models.PaymentReport)
admin.site.register(models.Coordinate)
admin.site.register(models.ColorHexFormat)
admin.site.register(models.SettingFormat)
admin.site.register(models.Download)
admin.site.register(models.RepositoryMediaFile)
admin.site.register(models.Repository)
admin.site.register(models.ExtraActivitieFile)
admin.site.register(models.ExtraActivitiePhoto)
admin.site.register(models.ExtraActivitieSchedule)
admin.site.register(models.ExtraActivitie, ExtrarActivitiesAdmin)

