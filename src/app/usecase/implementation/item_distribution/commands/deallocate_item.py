from sqlalchemy.orm import Session

from .....domain.item_distribution.implementation.commands.deallocate_item import DeallocateItemCommand

from .....infrastructure.models import ItemModel

from .....domain.item_distribution.item import ItemStatus

class DeallocateItemCommandImpl(DeallocateItemCommand):
    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def __call__(self, item_id):
        item_model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        if item_model == None:
            return
        
        item_model.order_id = None
        item_model.is_in_stock = True
        item_model.is_ready = True
        item_model.status = ItemStatus.OnStock.name