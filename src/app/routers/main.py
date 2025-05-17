from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.templating import Jinja2Templates

from ..infrastructure.database import SessionLocal
from ..infrastructure.navbar_info import get_navbar_info

from ..error import get_error

router = APIRouter(prefix='', tags=['Главная страница'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/')
def get_index_html(request: Request):
    with SessionLocal() as session:
        return templates.TemplateResponse(name='index.html', context={
            'request': request,
            "navbar_info": get_navbar_info(request, session),
        })

