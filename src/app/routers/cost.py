from fastapi import APIRouter, HTTPException, Body
from datetime import datetime, timedelta

from ..infrastructure.database import SessionLocal

from ..domain.product.rental_period import StartIsGreaterThanEndError, NegativeDurationError
from ..usecase.service.product import ProductDoesNotExistsError, WrongProductTypeError

from ..infrastructure.service.product import get_product_service

router = APIRouter(prefix="/api", tags=["Стоимость"])

@router.post("/get_cost_for_rent")
def get_cost_for_rent(
    product_id: int = Body(...),
    quantity: int = Body(...),
    start_date: str = Body(...),
    end_date: str = Body(...)
):
    with SessionLocal() as session:
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты")
        
        service = get_product_service(session)

        duration = end-start+timedelta(days=1)

        try:
            total_cost = service.get_cost_for_rent(
                product_id,
                duration,
                quantity
            )
        except ProductDoesNotExistsError:
            raise HTTPException(status_code=400, detail="Товар не найден")
        except WrongProductTypeError:
            raise HTTPException(status_code=400, detail="Данный товар не может быть использован для аренды")
        except (StartIsGreaterThanEndError, NegativeDurationError):
            raise HTTPException(status_code=400, detail="Дата начала аренды позже даты конца аренды")

        return {"total_cost": total_cost}
    
@router.post("/get_cost_for_sale")
def get_cost_for_sale(
    product_id: int = Body(...),
    quantity: int = Body(...)
):
    with SessionLocal() as session:
        service = get_product_service(session)

        try:
            total_cost = service.get_cost_for_sale(
                product_id,
                quantity
            )
        except ProductDoesNotExistsError:
            raise HTTPException(status_code=400, detail="Товар не найден")
        except WrongProductTypeError:
            raise HTTPException(status_code=400, detail="Данный товар не может быть использован для покупки")

        return {"total_cost": total_cost}