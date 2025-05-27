from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session

from .commands.create import CreateCartCommand
from .commands.add_to_cart import AddToCartCommand
from .commands.remove_from_cart import RemoveFromCartCommand
from .commands.clear_cart import ClearCartCommand

from .queries.get_cart_products import GetCartProductsQuery

from ..dto.cart import ProductInCartView

from ..product import ProductService

from .create.command import CartCreateCommand

class CartService:
    def __init__(
        self,
        session: Session,
        product_service: ProductService
    ):
        self.session = session
        self.product_service = product_service

    def create(
        self,
        user_id
    ):
        saga = CartCreateCommand(
            self.session,
            None
        )
        cart_id = saga(user_id)
        return cart_id
    
    def get_cart_products(self, user_id):
        rows = GetCartProductsQuery(self.session)(user_id)

        products = list()

        for row in rows:
            product_model, product_in_cart_model = row.tuple()
            product_id = product_model.id

            discount = self.product_service.get_discount(product_id)

            if product_model.is_for_rent_or_sale:
                duration = product_in_cart_model.end_rent-product_in_cart_model.start_rent+timedelta(days=1)
                standard_duration = timedelta(days=product_model.standard_rental_period)

                cost_with_discount = self.product_service.get_cost_for_rent(
                    product_id,
                    standard_duration
                )
                total_cost = self.product_service.get_cost_for_rent(
                    product_id,
                    duration,
                    product_in_cart_model.quantity
                )
            else:
                cost_with_discount = self.product_service.get_cost_for_sale(
                    product_id
                )
                total_cost = self.product_service.get_cost_for_sale(
                    product_id,
                    product_in_cart_model.quantity
                )

            product_view = ProductInCartView(
                product_in_cart_model.id,
                product_model.image,
                product_model.name,
                product_model.is_for_rent_or_sale,
                product_in_cart_model.start_rent,
                product_in_cart_model.end_rent,
                product_in_cart_model.quantity,
                product_model.rent_or_buy_cost,
                discount,
                cost_with_discount,
                total_cost
            )

            products.append(product_view)

        return products
    
    def add_to_cart(
        self,
        user_id,
        product_id,
        quantity: int,
        start_date: date,
        end_date: date
    ):
        model = AddToCartCommand(self.session)(
            user_id,
            product_id,
            quantity,
            start_date,
            end_date
        )

        return model
    
    def remove_from_cart(
        self,
        user_id,
        cart_item_id
    ):
        model = RemoveFromCartCommand(self.session)(user_id, cart_item_id)

        return model
    
    def clear_cart(
        self,
        user_id
    ):
        ClearCartCommand(self.session)(user_id)
    
    def make_order(
        self,
        user_id,
        order_service
    ):
        order_service.make_order(
            user_id
        )
        ClearCartCommand(self.session)(user_id)