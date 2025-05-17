from fastapi import APIRouter, Request, HTTPException, Query, Form
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from ..infrastructure.database import SessionLocal
from ..infrastructure.auth.session import get_current_user_id
from ..infrastructure.navbar_info import get_navbar_info
from ..infrastructure.service.order import get_order_service

from ..domain.wallet.wallet import NotEnoughMoneyError
from ..domain.order.order import WrongCurrentStatusOrderError
from ..domain.order.order import OrderStatus

from ..infrastructure.user_role import check_role, UserRole

router = APIRouter(prefix='', tags=['Заказы'])
templates = Jinja2Templates(directory='app/templates')

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50

@router.get("/orders")
def get_orders(request: Request):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        service = get_order_service(session)
        orders = service.get_user_orders(user_id)

        session.commit()

        return templates.TemplateResponse("orders.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "orders": orders
        })


@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, request: Request):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        service = get_order_service(session)
        order = service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
    
        session.commit()

        return templates.TemplateResponse("order_detail.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "order": order
        })


@router.post("/orders/{order_id}/pay")
def pay_order(order_id: int, request: Request):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise JSONResponse(status_code=401, detail="Вы не авторизованы")

        service = get_order_service(session)
        try:
            service.pay_order(user_id, order_id)
        except NotEnoughMoneyError as e:
            return JSONResponse(status_code=400, content={"detail": "Недостаточно средств на счету"})
        except WrongCurrentStatusOrderError as e:
            return JSONResponse(status_code=400, content={"detail": "Невозможно провести оплату, так как заказ уже оплачен или отменён"})
        except Exception:
            return JSONResponse(status_code=500, content={"detail": "Произошла ошибка"})

        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Оплата прошла успешно"})


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, request: Request):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise JSONResponse(status_code=401, detail="Вы не авторизованы")

        service = get_order_service(session)

        try:
            service.cancel_order_by_customer(user_id, order_id)
        except WrongCurrentStatusOrderError as e:
            return JSONResponse(status_code=400, content={"detail": "Невозможно отменить заказ, так как заказ уже отменён или оплачен"})
        except Exception:
            raise JSONResponse(status_code=400, detail="Невозможно отменить заказ")

        session.commit()
        return RedirectResponse(f"/orders/{order_id}", status_code=302)
    
@router.get("/all_orders", response_class=HTMLResponse)
def search_orders_by_id(
    request: Request,
    order_pattern: str = Query(default="", alias="order_pattern"),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)
):
    check_role(request, [UserRole.Employee, UserRole.Admin])
    with SessionLocal() as session:
        service = get_order_service(session)

        orders, total_count = service.get_all_orders_id_by_pattern(order_pattern, page, page_size)

        return templates.TemplateResponse("all_orders.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "orders": orders,
            "order_pattern": order_pattern,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        })
    
@router.get("/order_employee/{order_id}")
def order_for_employee(
    request: Request,
    order_id: str
):
    check_role(request, [UserRole.Employee, UserRole.Admin])
    with SessionLocal() as session:
        service = get_order_service(session)
        order = service.get_order_view_with_items_from_model(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        return templates.TemplateResponse("order_for_employee.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "order": order,
            "items": order.items
        })
    
@router.post("/order_employee/{order_id}/transfer")
def transfer_order(request: Request, order_id: int):
    check_role(request, [UserRole.Employee, UserRole.Admin])
    with SessionLocal() as session:
        service = get_order_service(session)

        try:
            service.transfer_order(order_id)
        except WrongCurrentStatusOrderError as e:
            return JSONResponse(status_code=400, content={"detail": "Невозможно передать, так как товар ещё не оплачен или отменён"})
        session.commit()
        return RedirectResponse(f"/order_employee/{order_id}", status_code=303)

@router.post("/order_employee/{order_id}/cancel")
def cancel_order(request: Request, order_id: int):
    check_role(request, [UserRole.Employee, UserRole.Admin])
    with SessionLocal() as session:
        service = get_order_service(session)
        try:
            service.cancel_order_by_employee(order_id)
        except WrongCurrentStatusOrderError as e:
            return JSONResponse(status_code=400, content={"detail": "Невозможно отменить, так как товар ещё уже отменён или оплачен"})
        session.commit()
        return RedirectResponse(f"/order_employee/{order_id}", status_code=303)

@router.post("/order_employee/{item_id}/return_item")
def return_item(
    request: Request,
    item_id: int,
    order_id: int = Form(...)
):
    check_role(request, [UserRole.Employee, UserRole.Admin])
    with SessionLocal() as session:
        service = get_order_service(session)
        service.return_item(order_id, item_id)
        session.commit()
        return RedirectResponse(f"/order_employee/{order_id}", status_code=303)