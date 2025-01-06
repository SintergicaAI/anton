import os
from functools import update_wrapper
from http.client import UNAUTHORIZED

from flask import request, Response


class Auth:
    @staticmethod
    def requires_password(operation):
        def wrapper(*args, **kwargs):
            password = request.headers.get("Authorization", "").replace("Basic ", "")
            if password != os.environ.get("PASSWORD"):
                return Response(status=UNAUTHORIZED)
            return operation(*args, **kwargs)
        return update_wrapper(wrapper, operation)
