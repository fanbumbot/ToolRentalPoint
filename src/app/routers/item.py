from datetime import date
from typing import Optional

from fastapi import APIRouter, Request, Response, Depends, HTTPException, Body, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from ..infrastructure.database import SessionLocal

from ..infrastructure.auth.session import get_current_user_id
from ..infrastructure.navbar_info import get_navbar_info
from ..infrastructure.service.item import get_item_service

from ..infrastructure.crud_router import add_crud_to_router

from ..domain.item_distribution.item_status import ItemStatus

filters = [
    {"name": "sticked_id", "placeholder": "Поиск по SID", "value": ""}
]

router = add_crud_to_router("item", get_item_service, filters, "Товар на складе")