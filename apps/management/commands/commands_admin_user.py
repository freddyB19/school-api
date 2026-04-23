from typing import TypeVar

from django.contrib.auth import get_user_model

from rest_framework import status as status_code

from pydantic import validate_call, ConfigDict

from apps.utils.result_commands import ResultCommand

from apps.management import models

User = TypeVar("User", bound = get_user_model())

from .utils.props import CreateUserParam

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def school_by_subdomain_exist(school_subdomain: str) -> ResultCommand:
	exist = models.Administrator.objects.filter(
		school__subdomain = school_subdomain
	).exists()

	return ResultCommand(status = True, query = exist)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_user(user: CreateUserParam):

	return ResultCommand(
		query = get_user_model().objects.create_user(
			name = user.name,
			email= user.email,
			password = user.password,
		)
	)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def add_admin_user_to_school(school_subdomain: str, user: CreateUserParam) -> ResultCommand:

	command_user = create_user(user)

	if not command_user.status:
		return command_user.errors

	admin = models.Administrator.objects.prefetch_related("users").filter(
		school__subdomain = school_subdomain
	).first()

	user = command_user.query 

	admin.users.add(user)

	return ResultCommand(status = True, query = user)
