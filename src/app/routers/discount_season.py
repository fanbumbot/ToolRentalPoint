from ..infrastructure.service.item import get_item_service

from ..infrastructure.crud_router import add_crud_to_router

from ..usecase.service.discount_season import DiscountSeasonService

filters = [
    {"name": "sticked_id", "placeholder": "Поиск по SID", "value": ""}
]

router = add_crud_to_router(
    "discount_season",
    lambda session: DiscountSeasonService(session),
    filters,
    "Сезон скидок")