from datetime import datetime, timezone

from fastapi import APIRouter, Request, Body, Response, HTTPException
from fastapi.templating import Jinja2Templates

from ..infrastructure.database import SessionLocal
from ..domain.user_auth.user import AlreadyRegisteredError
from ..domain.user_auth.login import LoginDoesNotMeetRequirementsError
from ..domain.user_auth.password import PasswordDoesNotMeetRequirementsError

from ..infrastructure.auth.session import get_current_user_id, auth_user, unauth_user
from ..usecase.service.user import LoginDoesNotExistError, WrongPasswordError

from ..error import get_error, post_error

from ..infrastructure.service.user import get_user_service

router = APIRouter(prefix='', tags=['Авторизация и регистрация'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/registration')
def get_registration_html(request: Request):
    return templates.TemplateResponse(name='registration.html', context={'request': request})

@router.get('/authorization')
def get_authorization_html(request: Request):
    return templates.TemplateResponse(name='authorization.html', context={'request': request})

@router.post("/registration")
def register(
    login: str = Body(),
    password: str = Body()
):
    try:
        with SessionLocal() as session:
            service = get_user_service(session)
            service.create(login, password)
            session.commit()

    except AlreadyRegisteredError:
        return post_error("Логин уже занят!!!")
    except LoginDoesNotMeetRequirementsError:
        return post_error("Логин должен содержать от 3 до 16 символов, в которые входят цифры и латинские буквы")
    except PasswordDoesNotMeetRequirementsError:
        return post_error("Пароль должен содержать от 3 до 16 символов, в которые входят цифры и латинские буквы")
    return post_error()

@router.post("/authorization")
def authorization(
    response: Response,
    login: str = Body(),
    password: str = Body()
):
    try:
        with SessionLocal() as session:
            service = get_user_service(session)
            auth_user(service, response, login, password)
            session.commit()
    except (LoginDoesNotExistError, WrongPasswordError):
        return post_error("Неверный логин или пароль")

    return post_error()

@router.post("/me")
def get_current_user(request: Request):
    return get_current_user_id(request)

@router.post("/logout")
def logout(response: Response):
    unauth_user(response)
    return post_error()
