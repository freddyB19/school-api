from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import Permission
from . import models

# Register your models here.
class AdminUser(UserAdmin):
	ordering = ["id"]

	list_display = [
		"id",
		"name",
		"email",
		"role",
	]

	list_filter = [
		"role"
	]

	fieldsets = [
		(
			None,
			{"fields": ("email", "password", "role", "user_permissions")}
		),
		(
			"Permissions",
			{"fields": ("is_admin" ,"is_staff", "is_active", "is_superadmin", "is_superuser")}
		)
	]
	add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("name", "role", "user_permissions", "email", "password1", "password2")
        }),
    )



admin.site.register(models.User, AdminUser)
admin.site.register(Permission)
