from datetime import date
from typing import Optional

from fastapi import APIRouter, Request, Response, Depends, HTTPException, Body, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..infrastructure.database import SessionLocal

from ..infrastructure.auth.session import get_current_user_id
from ..infrastructure.navbar_info import get_navbar_info
from ..infrastructure.service.cart import get_cart_service
from ..infrastructure.service.order import get_order_service

from ..usecase.service.order import NotEnoughItems
    

router = APIRouter(prefix='', tags=['Корзина'])
templates = Jinja2Templates(directory='app/templates')

@router.get("/cart")
def get_cart(request: Request):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        service = get_cart_service(session)
        cart_items = service.get_cart_products(user_id)

        return templates.TemplateResponse("cart.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "cart_items": cart_items
        })
    
@router.post("/cart/add")
def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None)
):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")
        
        if start_date != None and end_date != None:
            try:
                start_date = date.fromisoformat(start_date)
                end_date = date.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты")

        service = get_cart_service(session)
        service.add_to_cart(
            user_id,
            product_id,
            quantity,
            start_date,
            end_date
        )

        session.commit()
        return RedirectResponse("/cart", status_code=302)

@router.post("/cart/remove")
def remove_from_cart(
    request: Request,
    cart_item_id: int = Form(...)
):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")
        
        service = get_cart_service(session)
        service.remove_from_cart(user_id, cart_item_id)

        session.commit()
        return RedirectResponse("/cart", status_code=302)

@router.post("/cart/make_order")
def make_order(
    request: Request
):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        service = get_cart_service(session)
        order_service = get_order_service(session)
        try:
            service.make_order(user_id, order_service)
        except NotEnoughItems:

            cart_items = service.get_cart_products(user_id)
            return templates.TemplateResponse("cart.html", {
                "request": request,
                "navbar_info": get_navbar_info(request, session),
                "error_message": "Недостаточно товара на складе для оформления заказа.",
                "cart_items": cart_items
            })

        session.commit()
        return RedirectResponse("/orders", status_code=302)