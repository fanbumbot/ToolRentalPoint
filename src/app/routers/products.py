from typing import Union, Any
import io
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request, Query, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from fastapi.responses import StreamingResponse
import openpyxl

from ..infrastructure.navbar_info import get_navbar_info
from ..infrastructure.auth.session import get_current_user_id

from ..infrastructure.database import SessionLocal
from ..usecase.service.product.product_filter import ProductFilter, ProductOrderBy

from ..infrastructure.service.product import get_product_service

from ..infrastructure.crud_router import add_crud_to_router

from ..usecase.service.product import TooManySymbolsInReviewError, WrongScoreInReviewError, ReviewAlreadyExistsError
from ..usecase.service.product import MAX_POST_LEN

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 12

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Страницы товаров"])

def parse_cost(value: Union[str, None]):
    try:
        return int(value)
    except:
        return None
    
def parse_order_by(value: str):
    if value == "name":
        return ProductOrderBy.Name
    elif value == "cost":
        return ProductOrderBy.Cost
    else:
        return ProductOrderBy.Name

def parse_is_ascending(value: str):
   is_ascending = value == "asc"
   return is_ascending

def parse_category(value: str):
    try:
        return int(value)
    except:
        return None
    
def generate_filter(
    substring_find: str,
    min_cost_str: str,
    max_cost_str: str,
    order_by_str: str,
    order_str: str,
    category_str: str
):
    min_cost = parse_cost(min_cost_str.strip())
    max_cost = parse_cost(max_cost_str.strip())
    order_by = parse_order_by(order_by_str.strip())
    is_ascending = parse_is_ascending(order_str.strip())
    category_id = parse_category(category_str.strip())

    filter = ProductFilter(
        substring_find,
        category_id,
        min_cost,
        max_cost,
        order_by,
        is_ascending
    )

    return filter

def get_product_info(
    request: Request,
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    session: Session = None,
    error: str = None
):
    product_service = get_product_service(session)

    model = product_service.get_product_by_slug(slug)
    if model is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    product = product_service.get_product_view_from_model(model)
    reviews, total_reviews = product_service.get_product_reviews(product.id, page, page_size)
    total_score = product_service.get_product_total_score(product.id)

    now = datetime.now(timezone.utc)

    return templates.TemplateResponse("product_info.html", {
        "request": request,
        "navbar_info": get_navbar_info(request, session),
        "product": product,
        "reviews": reviews,
        "total_reviews": total_reviews,
        "total_score": round(total_score, 2) if total_score else None,
        "total_pages": (total_reviews + page_size) // page_size,
        "page": page,
        "page_size": page_size,
        "error": error,
        "now": now,
        "timedelta": timedelta
    })

@router.get("/products", response_class=HTMLResponse)
def list_products(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    substring_find: str = Query(default="", alias="substring_find"),
    min_cost_str: str = Query(default="", alias="min_cost"),
    max_cost_str: str = Query(default="", alias="max_cost"),
    order_by_str: str = Query(default="name", alias="order_by"),
    order_str: str = Query(default="asc", alias="order"),
    category_str: str = Query(default="", alias="category")
):
    with SessionLocal() as session:
        product_service = get_product_service(session)

        categories = product_service.get_all_categories()
        categories_dict: dict[str, Any] = {
            category.name: category.id for category in categories
        }

        filter = generate_filter(
            substring_find,
            min_cost_str,
            max_cost_str,
            order_by_str,
            order_str,
            category_str
        )

        products, total_count = product_service.get_products_by_filter(
            page, page_size, filter
        )

        return templates.TemplateResponse("products.html", {
            "request": request,
            "navbar_info": get_navbar_info(request, session),
            "products": products,
            "page": page,
            "page_size": page_size,
            "substring_find": substring_find,
            "total_pages": (total_count + page_size) // page_size,
            "min_cost": filter.min_cost,
            "max_cost": filter.max_cost,
            "order_by": "cost" if filter.order_by == ProductOrderBy.Cost else "name",
            "order": "asc" if filter.is_ascending else "desc",
            "all_categories": categories_dict,
            "selected_category_id": filter.category_id if filter.category_id != None else ""
        })

@router.get("/products/{slug}")
def get_product_page(
    request: Request,
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)
):
    with SessionLocal() as session:
        return get_product_info(request, slug, page, page_size, session)

@router.post("/post_product_review/{slug}")
def post_product_review(
    request: Request,

    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),

    comment: str = Form(...),
    score: int = Form(...),
):
    with SessionLocal() as session:
        user_id = get_current_user_id(request)
        if user_id == None:
            return get_product_info(
                request,
                slug,
                page,
                page_size,
                session,
                "Вы не авторизованы"
            )

        try:
            service = get_product_service(session)
            model = service.get_product_by_slug(slug)
            if model == None:
                return get_product_info(
                    request,
                    slug,
                    page,
                    page_size,
                    session,
                    "Не удалось найти товар"
                )
            
            service.post_review(user_id, model.id, comment, score)
            session.commit()

            return get_product_info(
                request,
                slug,
                page,
                page_size,
                session
            )
        
        except (TooManySymbolsInReviewError, WrongScoreInReviewError, ReviewAlreadyExistsError) as e:
            if isinstance(e, TooManySymbolsInReviewError):
                error = f"Максимальная длина отзыва: {MAX_POST_LEN} символов"
            elif isinstance(e, ReviewAlreadyExistsError):
                error = "Вы уже оставляли свой отзыв ранее"
            elif isinstance(e, WrongScoreInReviewError):
                error = "Оценка должна быть от 0 до 10"

            return get_product_info(
                request,
                slug,
                page,
                page_size,
                session,
                error
            )

@router.get("/products_export", response_class=StreamingResponse)
def export_products_to_excel(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    substring_find: str = Query(default="", alias="substring_find"),
    min_cost_str: str = Query(default="", alias="min_cost"),
    max_cost_str: str = Query(default="", alias="max_cost"),
    order_by_str: str = Query(default="name", alias="order_by"),
    order_str: str = Query(default="asc", alias="order"),
    category_str: str = Query(default="", alias="category")
):
    with SessionLocal() as session:
        product_service = get_product_service(session)
        filter = generate_filter(
            substring_find,
            min_cost_str,
            max_cost_str,
            order_by_str,
            order_str,
            category_str
        
        )
        stream = product_service.get_xlsx(filter)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=products_export.xlsx"}
        )

filters = [
    {"name": "sticked_id", "placeholder": "Поиск по SID", "value": ""}
]

add_crud_to_router("admin_product", get_product_service, filters, "Товар на витрине", router=router)