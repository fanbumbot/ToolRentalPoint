from ..product.product_bunch import ProductBunch, ProductReadyForRent, ProductReadyForSale
from .repository.item import ItemRepository

from .item import Item

class NotEnoughItemsError(Exception):
    pass

def allocate_items(owner_id, repository: ItemRepository, product_bunch: ProductBunch):
    allocated_items: list[Item] = list()
    for ready_product in product_bunch.products:
        product_id = ready_product.product.id
        quantity = ready_product.quantity

        items = repository.get_ready_items_query(product_id, quantity)

        if len(items) != quantity:
            for allocated_item in allocated_items:
                allocated_item.deallocate()
            raise NotEnoughItemsError

        for item in items:
            allocated_items.append(item)
            if isinstance(ready_product, ProductReadyForSale):
                item.allocate_for_sale(owner_id)
            elif isinstance(ready_product, ProductReadyForRent):
                item.allocate_for_rent(owner_id, ready_product.rent_period)

    for allocated_item in allocated_items:
        repository.update_item_command(allocated_item)

    return allocated_items

def deallocate_items(repository: ItemRepository, items: list[Item]):
    try:
        for item in items:
            item.deallocate()
    except:
        raise
    for item in items:
        repository.update_item_command(item)

def pay_for_items(repository: ItemRepository, items: list[Item]):
    try:
        for item in items:
            item.buy()
    except:
        raise
    for item in items:
        repository.update_item_command(item)

def return_rented_item(repository: ItemRepository, item: Item):
    item.return_rented()
    repository.update_item_command(item)

