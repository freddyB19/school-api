from django.contrib import admin

from . import models
# Register your models here.

@admin.register(models.Administrator)
class AdministradorModelAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"school__name",
	]
