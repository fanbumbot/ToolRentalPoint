from sqlalchemy.orm import Session

from .....domain.item_distribution.implementation.commands.update_item_status import UpdateItemStatusCommand

from .....domain.item_distribution.item_status import ItemStatus

from .....infrastructure.models import ItemModel

class UpdateItemStatusCommandImpl(UpdateItemStatusCommand):
    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def __call__(self, item_id, status: ItemStatus):
        model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        if model == None:
            return None
        
        model.status = status.name

        if status == ItemStatus.OnStock:
            model.is_ready = True
            model.is_in_stock = True
        elif status == ItemStatus.Allocated:
            model.is_ready = False
            model.is_in_stock = True
        else:
            model.is_in_stock = False
            model.is_ready = False
