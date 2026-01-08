from http import HTTPMethod
from datetime import datetime
from typing import TypeVar, TypedDict

from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import request as rest_request
from rest_framework import response, status

from apps.school import models
from . import serializers


Repository = TypeVar("Repository", bound = models.Repository)
Request = TypeVar("Request", bound = rest_request.Request)
ListUploadedFile = TypeVar("ListUploadedFile", bound = list[InMemoryUploadedFile])

class RepositoryDict(TypedDict):
	name_project: str
	description: str | None
	created: datetime
	updated: datetime
	media: ListUploadedFile | None

def update_repository_files(request: Request, instance: Repository) -> dict[str, int | RepositoryDict]:

	if request.method != HTTPMethod.PATCH:
		return None

	serializer = serializers.MSchoolRepositoryUpdateMediaRequest(
		instance,
		data=request.data,
		partial = True
	)

	serializer.is_valid(raise_exception=True)

	update_repository = serializer.save()

	return {
		"data" : serializers.MSchoolRepositoryResponse(update_repository).data,
		"status" : status.HTTP_202_ACCEPTED
	}

def delete_repository_files(request: Request, instance: Repository) -> dict[str, int]:
	if request.method != HTTPMethod.DELETE:
		return None

	instance.media.all().delete()

	return {
		"status": status.HTTP_204_NO_CONTENT
	}
