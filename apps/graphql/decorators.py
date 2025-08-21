from functools import wraps
from graphql.type.definition import GraphQLResolveInfo

from . import exceptions

def context(func):
	def decorator(func):
		def wrapper(*args, **kwargs):
			info = next(arg for arg in args if isinstance(arg, GraphQLResolveInfo))
			return func(info.context, *args, **kwargs)

		return wrapper

	return decorator


def user_authentication(auth_func):
	def decorator(func):
		@wraps(func)
		@context(func)
		def wrapper(context, *args, **kwargs):
			if auth_func(context.user):
				return func(*args, **kwargs)
			raise exceptions.IsAuthenticated

		return wrapper

	return decorator


login_required = user_authentication(lambda user: user.is_authenticated)