from ...domain.entity import EntityCQImpl
from ...usecase.implementation.item_distribution.commands.allocate_item import AllocateItemCommand, AllocateItemCommandImpl
from ...usecase.implementation.item_distribution.commands.deallocate_item import DeallocateItemCommand, DeallocateItemCommandImpl
from ...usecase.implementation.item_distribution.commands.update_item_status import UpdateItemStatusCommand, UpdateItemStatusCommandImpl

from ...usecase.service.item import ItemService

def get_item_service(session):
    item_impl = EntityCQImpl({
        AllocateItemCommand: AllocateItemCommandImpl(session),
        DeallocateItemCommand: DeallocateItemCommandImpl(session),
        UpdateItemStatusCommand: UpdateItemStatusCommandImpl(session)
    })
    
    item_service = ItemService(session, item_impl)

    return item_service