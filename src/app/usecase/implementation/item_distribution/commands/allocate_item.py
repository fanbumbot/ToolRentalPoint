from sqlalchemy.orm import Session

from .....domain.item_distribution.implementation.commands.allocate_item import AllocateItemCommand

from .....infrastructure.models import ItemModel

from .....domain.item_distribution.item import ItemStatus

class AllocateItemCommandImpl(AllocateItemCommand):
    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def __call__(self, item_id, order_id):
        item_model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        if item_model == None:
            return
        
        item_model.order_id = order_id