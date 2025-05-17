from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix='', tags=['Ошибка!'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/error')
def get_index_html(request: Request):
    return templates.TemplateResponse(name='main_error.html', context={'request': request})

@router.get('/error_not_found')
def get_index_html(request: Request):
    return templates.TemplateResponse(name='not_found_error.html', context={'request': request})