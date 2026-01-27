import datetime
from typing import TypeVar

from django.urls import reverse
from django.test import Client
from django.conf import settings
from django.contrib.auth import get_user_model

import jwt

UserModel = get_user_model()
User = TypeVar("User", bound = UserModel)

ALGOTITHM = settings.STRAWBERRY_DJANGO_AUTH_TOKEN['ALGORITHM']
SECRET_KEY =  settings.STRAWBERRY_DJANGO_AUTH_TOKEN['STRAWBERRY_KEY']

PAYLOAD_SET_EXP = lambda time={"hours": 1}: datetime.datetime.utcnow() + datetime.timedelta(**time)            

def create_token(user_id: int) -> str:
	return jwt.encode(
		{"user_id": user_id},
		SECRET_KEY,
		algorithm = ALGOTITHM
	)

def encode_token(user: User, exp_time:datetime = None) -> str:
	payload = {
		"user_id": user.id,
		"exp": PAYLOAD_SET_EXP() if not exp_time else exp_time
	}

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
