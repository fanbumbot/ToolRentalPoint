from ..infrastructure.crud_router import add_crud_to_router

from ..usecase.service.category import CategoryService

filters = [
    {"name": "sticked_id", "placeholder": "Поиск по SID", "value": ""}
]

router = add_crud_to_router(
    "admin_categorie",
    lambda session: CategoryService(session),
    filters,
    "Категории товара")