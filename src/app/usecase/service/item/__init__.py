from sqlalchemy.orm import Session
from sqlalchemy import and_

from ....domain.entity import EntityCQImpl

from ....infrastructure.models import OrderModel, OrderAndProductModel, ItemModel, ProductModel, CartAndProductModel, CartModel
from ....domain.item_distribution.item import ItemStatus, Item

from ...base_crud_service import BaseCRUDService

from ..dto.crud.item import ItemCreateDTO, ItemEditDTO, ItemLongViewDTO, ItemShortViewDTO

class ItemService(BaseCRUDService):
    def __init__(
        self,
        session: Session,
        item_impl: EntityCQImpl
    ):
        super().__init__(session, ItemModel,
            ItemCreateDTO, ItemEditDTO, ItemLongViewDTO, ItemShortViewDTO)

        self.session = session
        self.item_impl = item_impl

    def create_item(self, sticked_id: str, product_id):
        model = ItemModel(
            sticked_id = sticked_id,
            product_id = product_id,
            status = ItemStatus.Unknown,
            is_in_stock = False,
            is_ready = False,
            order_id = None
        )
        self.session.add(model)
    
    def load_item_domain(self, item_id):
        item_model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        if item_model == None:
            return None
        
        product_model = self.session.query(ProductModel).filter(
            ProductModel.id == item_model.product_id
        ).one_or_none()

        if product_model == None:
            return None

        item = Item(
            item_model.id,
            self.item_impl,
            not product_model.is_for_rent_or_sale,
            product_model.is_for_rent_or_sale,
            ItemStatus[item_model.status]
        )

        return item

    def is_enough_items_for_order(self, cart_id):
        all_rows = self.session.query(CartAndProductModel).filter(
            CartAndProductModel.cart_id == cart_id
        ).all()

        total_product_quantity = dict()
        for row in all_rows:
            product_id = row.product_id
            if product_id in total_product_quantity:
                total_product_quantity[product_id] += row.quantity
            else:
                total_product_quantity[product_id] = row.quantity

        for product_id, required_quantity in total_product_quantity.items():
            current_quantity = self.session.query(ItemModel).filter(
                and_(
                    ItemModel.is_in_stock,
                    ItemModel.is_ready,
                    ItemModel.product_id == product_id
                )
            ).count()
            if current_quantity < required_quantity:
                return False
        return True

    def allocate_for_order(self, order_id):
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        
        if order_model == None:
            return None
        
        user_id = order_model.user_id

        order_product_models = self.session.query(OrderAndProductModel).filter(
            OrderAndProductModel.order_id == order_id
        ).all()

        for model in order_product_models:
            all_suitable_items = self.session.query(ItemModel.id).filter(
                and_(
                    ItemModel.product_id == model.product_id,
                    ItemModel.status == ItemStatus.OnStock.name
                )
            ).limit(model.quantity).all()
            
            for item_model in all_suitable_items:
                item = self.load_item_domain(item_model.tuple()[0])
                if item == None:
                    continue

                if item.can_be_rented:
                    item.allocate_for_rent(order_id, user_id)
                else:
                    item.allocate_for_sale(order_id, user_id)

    def deallocate_from_order(self, order_id):
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()

        if order_model == None:
            return None

        items = self.session.query(ItemModel.id).filter(
            ItemModel.order_id == order_model.id
        ).all()

        for item_row in items:
            item_id = item_row.tuple()[0]
            item = self.load_item_domain(item_id)
            item.deallocate()
        
    def return_item(self, item_id):
        model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        if model == None:
            return
        
        model.is_in_stock = True
        model.is_ready = True
        model.order_id = None
        model.status = ItemStatus.OnStock.name

    def get_product_items_count(self, product_id):
        count = self.session.query(ItemModel).filter(
            and_(
                ItemModel.product_id == product_id,
                ItemModel.is_in_stock,
                ItemModel.is_ready
            )
        ).count()
        return count
    
    """
    def get_all(self, pattern_sticked_id: str, page: int, page_size: int):
        query = self.session.query(ItemModel).filter(
            ItemModel.sticked_id.ilike(f"%{pattern_sticked_id.strip()}%")
        )

        total_count = query.count()
        
        models = query.offset((page - 1) * page_size).limit(page_size).all()
        return models, total_count
    
    def get_item_model_by_id(self, item_id):
        model = self.session.query(ItemModel).filter(
            ItemModel.id == item_id
        ).one_or_none()

        return model
    """