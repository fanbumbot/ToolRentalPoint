from fastapi import APIRouter, Request, Body, Response, HTTPException, Form
from fastapi.templating import Jinja2Templates

from ..infrastructure.navbar_info import get_navbar_info, get_current_user_id

from ..infrastructure.database import SessionLocal

from ..infrastructure.service.user import get_user_service
from ..domain.money.money import MoneyAmountIsNotPositive

router = APIRouter(prefix='', tags=['Авторизация и регистрация'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/wallet')
def get_wallet_html(request: Request):
    with SessionLocal() as session:

        if not get_current_user_id(request):
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        return templates.TemplateResponse(name='wallet.html', context={
            'request': request,
            'navbar_info': get_navbar_info(request, session)
        })
    

@router.post("/wallet/top_up")
def post_top_up(
    request: Request,
    amount: int = Form(...)
):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        wallet_service = get_user_service(session)

        try:
            wallet_service.top_up_wallet(user_id, amount)
        except MoneyAmountIsNotPositive:
            return templates.TemplateResponse("wallet.html", {
                "request": request,
                "error_message": "Сумма должна быть больше нуля",
                "navbar_info": get_navbar_info(request, session)
            })
        
        session.commit()

        return templates.TemplateResponse("wallet.html", {
            "request": request,
            "success_message": f"Кошелёк пополнен на {amount} ₽",
            "navbar_info": get_navbar_info(request, session)
        })