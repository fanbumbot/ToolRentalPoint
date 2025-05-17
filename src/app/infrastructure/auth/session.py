from datetime import datetime, timezone

from fastapi import Response, Request

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from .consts import *
from .exceptions import *

from ...usecase.service.user import UserService

from .token import generate_access_token, decode_token

def auth_user(user_auth_service: UserService, response: Response, login: str, password: str):    
    user_auth_service.log_in(login, password)

    user_model = user_auth_service.get_model_by_login(login)
    token = generate_access_token(user_model.id, user_model.login)
    response.set_cookie(key=TOKEN_NAME, value=token, httponly=True)

def unauth_user(response: Response):
    response.delete_cookie(TOKEN_NAME, httponly=True)

def get_current_user_id(request: Request):
    token = request.cookies.get(TOKEN_NAME)
    if not token:
        return None

    user_id, _, exp = decode_token(token)

    expire_time = datetime.fromtimestamp(exp, tz=timezone.utc)
    if expire_time < datetime.now(timezone.utc):
        raise TokenTimeOutError

    return user_id