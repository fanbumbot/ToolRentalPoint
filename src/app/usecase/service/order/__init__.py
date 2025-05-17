from sqlalchemy.orm import Session
from sqlalchemy import func, and_, String
from sqlalchemy.sql.expression import cast

from datetime import datetime, time, timezone, timedelta

from .create.command import CreateOrderCommand

from ....domain.entity import EntityCQImpl

from ..user import UserService
from ..product import ProductService
from ..item import ItemService

from ....infrastructure.models import UserModel, OrderModel, OrderAndProductModel, CartModel, ItemModel

from ..dto.order import OrderView, OrderProductView, OrderItemView, OrderWithItemsView

from ....domain.order.order import Order, OrderStatus, Money

TIME_TO_PAY_ORDER_IN_MINUTES = 15

class WrongUserError(Exception):
    pass

class NotEnoughItems(Exception):
    pass

class UserDoesNotHaveCart(Exception):
    pass

class OrderService:
    def __init__(
        self,
        session: Session,
        order_impl: EntityCQImpl,
        user_service: UserService,
        product_service: ProductService,
        item_service: ItemService
    ):
        self.session = session
        self.order_impl = order_impl
        self.user_service = user_service
        self.product_service = product_service
        self.item_service = item_service

    def make_order(
        self,
        user_id
    ):
        cart_model = self.session.query(CartModel).filter(
            CartModel.user_id == user_id
        ).one_or_none()
        if cart_model == None:
            raise UserDoesNotHaveCart

        if not self.is_enough_items_for_order(cart_model.id):
            raise NotEnoughItems

        wallet = self.user_service.get_wallet(user_id)

        order_id = CreateOrderCommand(
            self.session,
            self.order_impl,
            wallet
        )(user_id)

        self.item_service.allocate_for_order(order_id)

        return order_id
    
    def is_enough_items_for_order(self, cart_id):
        return self.item_service.is_enough_items_for_order(cart_id)
    
    def get_order_total_cost(self, order_id):
        models = self.session.query(OrderAndProductModel).filter(
            OrderAndProductModel.order_id == order_id
        ).all()

        total_cost = 0
        for model in models:
            if model.end_rent != None and model.start_rent != None:
                duration = model.end_rent-model.start_rent
            else:
                duration = None
            cost = self.product_service.get_any_cost(
                model.product_id,
                duration,
                model.quantity
            )
            total_cost += cost

        return total_cost
    
    def load_order_domain(self, order_id):
        model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        if model == None:
            return None
        
        wallet = self.user_service.get_wallet(model.user_id)
        total_cost = self.get_order_total_cost(order_id)

        status = OrderStatus[model.status]

        order = Order(
            model.id,
            self.order_impl,
            status,
            Money(total_cost),
            wallet
        )

        return order

    def get_order_view_from_model(self, order_model: OrderModel, with_products: bool = False):
        models = self.session.query(OrderAndProductModel).filter(
            OrderAndProductModel.order_id == order_model.id
        ).all()

        self.cancel_if_time_expired(order_model.id)

        items = list()
        total_cost = 0
        for model in models:
            if model.end_rent != None and model.start_rent != None:
                duration = model.end_rent-model.start_rent
            else:
                duration = None
            cost = self.product_service.get_any_cost(
                model.product_id,
                duration,
                model.quantity
            )
            total_cost += cost

            if with_products:
                product_model = self.product_service.get_product_model_by_id(model.product_id)
                if model.end_rent != None and model.start_rent != None:
                    duration = (datetime.combine(model.end_rent, datetime.min.time())-
                                datetime.combine(model.start_rent, datetime.min.time()))
                else:
                    duration = None

                product_initial_cost = self.product_service.get_initial_cost(model.product_id)
                product_cost = self.product_service.get_any_cost(model.product_id)
                product_total_cost = self.product_service.get_any_cost(
                    model.product_id,
                    duration,
                    model.quantity
                )

                product_discount = self.product_service.get_discount(model.product_id)

                order_item_model = OrderProductView(
                    model.id,
                    product_model.image,
                    product_model.name,
                    product_model.is_for_rent_or_sale,
                    model.start_rent,
                    model.end_rent,
                    model.quantity,
                    product_initial_cost,
                    product_cost,
                    product_discount,
                    product_total_cost
                )
                items.append(order_item_model)

        now = datetime.now(timezone.utc)
        time_left_for_payment = TIME_TO_PAY_ORDER_IN_MINUTES - (now-order_model.registration_datetime.replace(tzinfo=timezone.utc)).seconds//60

        view = OrderView(
            order_model.id,
            total_cost,
            order_model.status,
            items,
            time_left_for_payment
        )

        return view
    
    def get_order_view_with_items_from_model(self, order_id):
        item_models = self.session.query(ItemModel).filter(
            ItemModel.order_id == order_id
        ).all()

        item_views = list()
        for item_model in item_models:
            product_model = self.product_service.get_product_model_by_id(item_model.product_id)
            item_view = OrderItemView(
                item_model.id,
                item_model.sticked_id,
                product_model.image,
                product_model.name
            )

            item_views.append(item_view)

        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        
        if order_model == None:
            return None
        
        view = OrderWithItemsView(
            order_model.id,
            order_model.status,
            item_views
        )

        return view
    
    def get_user_orders(self, user_id):
        models = self.session.query(OrderModel).filter(
            OrderModel.user_id == user_id
        ).all()

        order_views = list()
        for model in models:
            view = self.get_order_view_from_model(model)
            order_views.append(view)

        return order_views
    
    def get_all_orders_id_by_pattern(self, order_pattern: str, page: int, page_size: int):
        offset = (page - 1) * page_size
        all_orders = self.session.query(OrderModel.id).filter(
            cast(OrderModel.id, String).like(f"%{order_pattern}%")
        )
        total_count = all_orders.count()
        order_rows = all_orders.offset(offset).limit(page_size).all()

        orders_by_id: list[int] = list()
        for row in order_rows:
            id = row.tuple()[0]
            orders_by_id.append(id)

        return orders_by_id, total_count
    
    def get_order_by_id(self, order_id):
        model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        view = self.get_order_view_from_model(model, True)
        return view
    
    def get_order_with_items_by_id(self, order_id):
        model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        view = self.get_order_view_with_items_from_model(model)
        return view
    
    def is_user_order_owner(self, user_id, order_id):
        model = self.session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).one_or_none()
        if model == None:
            return False
        return model.user_id == user_id
    
    def pay_order(self, user_id, order_id):
        if not self.is_user_order_owner(user_id, order_id):
            raise WrongUserError
        
        self.cancel_if_time_expired(order_id)
        
        order = self.load_order_domain(order_id)
        order.pay()

    def cancel_order_by_customer(self, user_id, order_id):
        if not self.is_user_order_owner(user_id, order_id):
            raise WrongUserError

        self.item_service.deallocate_from_order(order_id)

        order = self.load_order_domain(order_id)
        order.deny_by_customer()

    def cancel_order_by_employee(self, order_id):
        self.item_service.deallocate_from_order(order_id)

        order = self.load_order_domain(order_id)
        order.deny_by_employee()

    def cancel_order_by_system(self, order_id):
        self.item_service.deallocate_from_order(order_id)

        order = self.load_order_domain(order_id)
        order.deny_by_system()

    def cancel_all_with_expired_time(self):
        now = datetime.now(timezone.utc)
        rows = self.session.query(OrderModel.id).filter(
            and_(
                OrderModel.status == OrderStatus.AwaitingPayment.name,
                now-OrderModel.registration_datetime > timedelta(minutes=TIME_TO_PAY_ORDER_IN_MINUTES)
            )
        ).all()

        for row in rows:
            id = row.tuple()[0]
            self.cancel_order_by_system(id)

    def cancel_if_time_expired(self, order_id):
        now = datetime.now(timezone.utc)
        order_model = self.session.query(OrderModel).filter(
            and_(
                OrderModel.id == order_id,
                OrderModel.status == OrderStatus.AwaitingPayment.name,
                OrderModel.registration_datetime < now.replace(tzinfo=None)-timedelta(minutes=TIME_TO_PAY_ORDER_IN_MINUTES)
            )
        ).one_or_none()
        if order_model == None:
            return
        
        self.cancel_order_by_system(order_model.id)

    def transfer_order(self, order_id):
        order = self.load_order_domain(order_id)
        order.transfer_items()

    def return_item(self, order_id, item_id):
        self.item_service.return_item(item_id)

        