from django.contrib import admin
from . import models

# Register your models here.
class AdminUser(admin.ModelAdmin):
	list_display = [
		"id",
		"name",
		"email",
		"role"
	]

	list_filter = [
		"role"
	]



admin.site.register(models.User, AdminUser)