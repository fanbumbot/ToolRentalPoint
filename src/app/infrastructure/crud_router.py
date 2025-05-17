from typing import Callable

from sqlalchemy.orm import Session

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .database import SessionLocal

from ..usecase.base_crud_service import BaseCRUDService
from ..usecase.service.dto.crud.base.crud_base_dto import FormErrors, FieldValidationError

from .navbar_info import get_navbar_info

async def parse_form_data(request: Request):
    form = await request.form()
    return dict(form)

def add_crud_to_router(
    entity_name: str,
    get_service_func: Callable[[Session], BaseCRUDService],
    filters: list[dict],
    title: str,
    template_prefix: str = "crud",
    router = APIRouter()
):
    templates = Jinja2Templates(directory='app/templates')

    @router.get(f"/{entity_name}s", response_class=HTMLResponse)
    def get_list(request: Request, page: int = 1, page_size: int = 50):
        with SessionLocal() as session:
            service = get_service_func(session)
            items, total_count = service.get_all(page, page_size)
            return templates.TemplateResponse(f"{template_prefix}/list.html", {
                "request": request,
                "navbar_info": get_navbar_info(request, session),
                "entity_name": entity_name,
                "title": title,
                "filters": filters,
                "items": items,
                "fields": service.short_view_dto_type.get_fields(),
                "page": page,
                "total_pages": (total_count + page_size) // page_size,
            })
        
    @router.get(f"/{entity_name}_details/{{id}}", response_class=HTMLResponse)
    def get_detail(request: Request, id: int):
        with SessionLocal() as session:
            service = get_service_func(session)
            item = service.get_detail(id)
            return templates.TemplateResponse(f"{template_prefix}/details.html", {
                "request": request,
                "navbar_info": get_navbar_info(request, session),
                "entity_name": entity_name,
                "title": title,
                "item": item,
                "fields": service.long_view_dto_type.get_fields()
            })

    @router.get(f"/{entity_name}_edit/", response_class=HTMLResponse)
    def create_form(request: Request):
        with SessionLocal() as session:
            service = get_service_func(session)
            return templates.TemplateResponse(f"{template_prefix}/form.html", {
                "request": request,
                "navbar_info": get_navbar_info(request, session),
                "entity_name": entity_name,
                "title": title,
                "fields": service.create_dto_type.get_fields(),
                "item": None
            })

    @router.get(f"/{entity_name}_edit/{{id}}", response_class=HTMLResponse)
    def edit_form(request: Request, id: int):
        with SessionLocal() as session:
            service = get_service_func(session)
            item = service.get_edit_dto(id)
            return templates.TemplateResponse(f"{template_prefix}/form.html", {
                "request": request,
                "navbar_info": get_navbar_info(request, session),
                "entity_name": entity_name,
                "title": title,
                "fields": service.edit_dto_type.get_fields(),
                "item": item
            })

    @router.post(f"/{entity_name}_edit/", response_class=HTMLResponse)
    @router.post(f"/{entity_name}_edit/{{id}}", response_class=HTMLResponse)
    def save(
        request: Request,
        id: int = None,
        form_data: dict = Depends(parse_form_data)
    ):
        with SessionLocal() as session:
            service = get_service_func(session)
            try:
                if id:
                    service.update(id, form_data)
                else:
                    service.create(form_data)
            except (FieldValidationError, FormErrors) as e:
                if isinstance(e, FormErrors):
                    errors = e.errors
                    main_error = None
                else:
                    errors = None
                    main_error = e.message
                if id:
                    item = service.get_edit_dto(id)
                    return templates.TemplateResponse(f"{template_prefix}/form.html", {
                        "request": request,
                        "navbar_info": get_navbar_info(request, session),
                        "title": title,
                        "errors": errors,
                        "main_error": main_error,
                        "entity_name": entity_name,
                        "fields": service.edit_dto_type.get_fields(),
                        "item": item
                    })
                else:
                    return templates.TemplateResponse(f"{template_prefix}/form.html", {
                        "request": request,
                        "navbar_info": get_navbar_info(request, session),
                        "title": title,
                        "errors": errors,
                        "main_error": main_error,
                        "entity_name": entity_name,
                        "fields": service.create_dto_type.get_fields(),
                        "item": None
                    })
            session.commit()
            return RedirectResponse(f"/{entity_name}s", status_code=303)

    @router.post(f"/{entity_name}_delete/{{id}}")
    def delete(id: int):
        with SessionLocal() as session:
            get_service_func(session).delete(id)
            session.commit()
            return RedirectResponse(f"/{entity_name}s", status_code=303)

    return router