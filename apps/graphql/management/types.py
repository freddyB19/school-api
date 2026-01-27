from typing import Annotated

from django.contrib.auth import get_user_model

import strawberry, strawberry_django
from strawberry import auto
from strawberry_django.pagination import OffsetPaginated

from apps.management import models
from apps.school import models as school_models

@strawberry_django.type(school_models.School)
class SchoolAdministration:
	id: auto
	name: auto
	subdomain: auto

@strawberry_django.type(get_user_model())
class User:
	id: auto
	name: auto
	email: auto
	date_joined: auto
	last_login: auto


@strawberry_django.type(models.Administrator)
class Administrator:
	id: auto
	users: OffsetPaginated[User] = strawberry_django.offset_paginated()
	school: SchoolAdministration


@strawberry.type
class ErrorCode:
	code: str | None
	status: int | None

@strawberry.type
class AdminErrorResponse:
	kind: str
	message: str
	code: ErrorCode | None

@strawberry.type
class AdminResponse:
	messages: list[AdminErrorResponse]


Response = Annotated[Administrator | AdminResponse, strawberry.union("AdministratorResponse")]

__all__ = [
	"Administrator",
	"ErrorCode",
	"AdminErrorResponse",
	"AdminResponse",
	"Response"
]