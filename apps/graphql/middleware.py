
from .utils import (
    get_user,
    get_payload,
    get_http_authorization,
)

class AuthorizationMiddleware:

    def resolve(self, next, root, info, **kwargs):
        context = info.context

        token = get_http_authorization(request = context)
        
        if token:
            data_token = get_payload(token)

            user = get_user(data_token)

            if user:
            
                info.context.user = user

        return next(root, info, **kwargs)