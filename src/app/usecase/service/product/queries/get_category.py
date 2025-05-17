from sqlalchemy.orm import Session

from .....infrastructure.models import CategoryModel

class GetCategoryQuery:
    def __call__(
        self,
        session: Session,
        category_id
    ):
        return session.query(CategoryModel).filter(CategoryModel.id == category_id).one_or_none()