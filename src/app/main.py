from .infrastructure import *
create_all_tables()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), name='static')

from app.routers.error import router as error_router
app.include_router(error_router)

@app.exception_handler(Exception)
def exception_handler(request, exc):
    return RedirectResponse("/error")

@app.exception_handler(404)
def exception_handler(request, exc):
    return RedirectResponse("/error_not_found")




from app.routers.main import router as main_router
from app.routers.auth import router as auth_reg_router
from app.routers.cost import router as cost_router
from app.routers.products import router as products_router
from app.routers.cart import router as cart_router
from app.routers.order import router as order_router
from app.routers.wallet import router as wallet_router

from app.routers.item import router as item_router
from app.routers.discount_season import router as discount_season_router
from app.routers.discount import router as discount_router
from app.routers.category import router as category_router

app.include_router(main_router)
app.include_router(auth_reg_router)
app.include_router(cost_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(wallet_router)
app.include_router(item_router)
app.include_router(discount_season_router)
app.include_router(discount_router)
app.include_router(category_router)

from .infrastructure.cancel_order_background_task import run_cancel_order_background_task

run_cancel_order_background_task()