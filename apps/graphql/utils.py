from typing import TypeVar

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.handlers.asgi import ASGIRequest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

import jwt

from pydantic import validate_call, ConfigDict

from . import exceptions


WRequest = TypeVar("WRequest", bound=WSGIRequest)
ARequest = TypeVar("WRequest", bound=ASGIRequest)

UserModel = get_user_model()

HEADER_NAME = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['JWT_AUTH_HEADER_NAME']
HEADER_PREFIX = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['JWT_AUTH_HEADER_PREFIX']
ALGOTITHM = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['ALGORITHM']
SECRET_KEY =  settings.STRAWBERRY_DJANGO_AUTH_TOKEN['STRAWBERRY_KEY']


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed=True))
def get_http_authorization(request: WRequest | ARequest) -> str | None:
    header = request.headers.get(HEADER_NAME, "")
    
    if not isinstance(header, str):
        return None
    if not header.startswith(HEADER_PREFIX):
        return None

    return header.split()[1]

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
    return UserModel.objects.filter(pk = id).first()

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_user_by_payload(payload: dict) -> UserModel | AnonymousUser:
    KEY_USER_ID= "user_id"

    if not KEY_USER_ID in payload:
        return AnonymousUser()
        
    user = get_user_by_id(id = payload.get(KEY_USER_ID))

    if not user or not user.is_active:
        return AnonymousUser()

    return user

def get_user_from_token(request: WRequest | ARequest) -> UserModel | AnonymousUser:
    token = get_http_authorization(request = request)

    if not token:
        return AnonymousUser()

    try:
        payload = decode_token(token)
    except exceptions.JWTDecodeError as error:
        return AnonymousUser()

    return get_user_by_payload(payload = payload)
