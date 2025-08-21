import datetime
from typing import TypeVar

from django.conf import settings
from django.contrib.auth import get_user_model

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
