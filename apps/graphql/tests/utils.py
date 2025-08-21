import datetime
from typing import TypeVar

from django.urls import reverse
from django.test import Client
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.user.tests.utils.utils import FakerCreateUser

import jwt

UserModel = get_user_model()
User = TypeVar("User", bound = UserModel)

ALGOTITHM = settings.GRAPHENE_JWT['ALGORITHM']
SECRET_KEY =  settings.GRAPHENE_JWT['GRAPHENE_PRIVATE_KEY'] or settings.GRAPHENE_JWT['GRAPHENE_KEY']

PAYLOAD_SET_EXP = lambda time={"hours": 1}: datetime.datetime.utcnow() + datetime.timedelta(**time)


def encode_token(user: User, exp_time:dict = None) -> str:
	payload = {
		"user_id": user.id,
		"exp": PAYLOAD_SET_EXP()
	}
	if exp_time:
		payload.update({"exp": exp_time})

	return jwt.encode(
		payload, 
		SECRET_KEY, 
		algorithm = ALGOTITHM
	)


def get_token(email: str = "auth@example.com", password: str = "1234") -> str:
	client = Client()

	response = client.post(reverse("user:obtain_token_pair"), {
		"email": email,
		"password": password
	})

	return response.data["access"]