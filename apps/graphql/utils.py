from typing import TypeVar

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest

import jwt

from graphql import GraphQLError
from pydantic import validate_call, ConfigDict

from . import exceptions


WRequest = TypeVar("WRequest", bound=WSGIRequest)

UserModel = get_user_model()

PAYLOAD_GET_USER_ID = lambda payload: payload.get("user_id")

HEADER_NAME = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_NAME']
HEADER_PREFIX = settings.GRAPHENE_JWT['JWT_AUTH_HEADER_PREFIX']
ALGOTITHM = settings.GRAPHENE_JWT['ALGORITHM']
SECRET_KEY =  settings.GRAPHENE_JWT['GRAPHENE_PRIVATE_KEY'] or settings.GRAPHENE_JWT['GRAPHENE_KEY']


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed=True))
def get_http_authorization(request: WRequest):
    auth = request.META.get(HEADER_NAME, "").split()

    if len(auth) != 2 or HEADER_PREFIX.lower() != auth[0].lower():
        return None

    return auth[1]


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def decode_token(token: str) -> dict:
    message = "" 
    
    try:

        return jwt.decode(token, SECRET_KEY, algorithms=ALGOTITHM)
    
    except jwt.ExpiredSignatureError:
        message = exceptions.JWT_ERROR_MESSAGE_EXPIRED
    except  jwt.InvalidSignatureError:
        message = exceptions.JWT_ERROR_MESSAGE_INVALID
    except jwt.ImmatureSignatureError:
        message = exceptions.JWT_ERROR_MESSAGE_IMMATURE
    except jwt.DecodeError:
        message = exceptions.JWT_ERROR_MESSAGE_DECODE

    raise exceptions.JWTDecodeError(message)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_user_by_id(id: int) -> UserModel | None:
    try:
        return UserModel.objects.get(pk = id)
    except UserModel.DoesNotExist as e:
        return None


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_user_by_payload(payload: dict) -> UserModel:
    
    userId = PAYLOAD_GET_USER_ID(payload)

    if not userId:
        raise exceptions.InvalidPayload
    
    user = get_user_by_id(userId)

    if not user:
        raise exceptions.InvalidUser

    if not user.is_active:
        raise exceptions.UserIsNotActive

    return user


def get_payload(token: str) -> dict:
	try:
		return decode_token(token)
	except exceptions.JWTDecodeError as e:
		raise GraphQLError(str(e))


def get_user(payload: dict) -> UserModel | None:
	try:
		return get_user_by_payload(payload)
	except (exceptions.InvalidPayload, exceptions.InvalidUser, exceptions.UserIsNotActive) as e:
		return None