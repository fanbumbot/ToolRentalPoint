from ..infrastructure.crud_router import add_crud_to_router

from ..usecase.service.discount import DiscountService

filters = [
    {"name": "sticked_id", "placeholder": "Поиск по SID", "value": ""}
]

router = add_crud_to_router(
    "discount",
    lambda session: DiscountService(session),
    filters,
    "Скидки")