from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import openpyxl
import io

import re

from ....infrastructure.models import ProductModel, DiscountModel, DiscountPeriodModel, CategoryModel
from ....infrastructure.models import ProductReviewModel, UserModel

from ....domain.entity import EntityCQImpl

from ....domain.product.product import Product
from ....domain.product.rental_period import RentalPeriodDuration
from ....domain.product.cost import Cost
from ....domain.product.quantity import Quantity
from ....domain.discount.discount import Discount
from ....domain.discount.discount_value import DiscountValue

from .queries.get_products import GetProductsQuery
from .queries.get_category import GetCategoryQuery

from .create.saga import ProductCreateSaga

from ..dto.product import ProductView

from .product_filter import ProductFilter

from .create.command import ProductCreateCommand

from ..item import ItemService

from ..dto.review import ProductReviewView

from ...base_crud_service import BaseCRUDService
from ..dto.crud.product import ProductCreateDTO, ProductEditDTO, ProductLongViewDTO, ProductShortViewDTO, ProductModel

MAX_POST_LEN = 256

class WrongProductTypeError(Exception):
    pass

class ProductDoesNotExistsError(Exception):
    pass

class WrongScoreInReviewError(Exception):
    pass

class TooManySymbolsInReviewError(Exception):
    pass

class ReviewAlreadyExistsError(Exception):
    pass

class ProductService(BaseCRUDService):
    def __init__(
        self,
        session: Session,
        item_service: ItemService,
        product_impl: EntityCQImpl,
        discount_impl: EntityCQImpl
    ):
        super().__init__(session, ProductModel,
            ProductCreateDTO, ProductEditDTO, ProductLongViewDTO, ProductShortViewDTO)
        self.session = session
        self.item_service = item_service
        self.product_impl = product_impl
        self.discount_impl = discount_impl

    def __create(
        self,
        slug: str,
        category_id,
        name: str,
        description: str,
        image: str,
        rent_or_buy_cost: int,
        standard_rental_period: timedelta,
        is_for_rent_or_sale: bool
    ):
        product_id = ProductCreateCommand(
            self.session, self.product_impl
        )(
            slug,
            category_id,
            name,
            description,
            image,
            rent_or_buy_cost,
            standard_rental_period,
            is_for_rent_or_sale
        )
        
        return product_id
    
    def load_product_domain(self, product_id):
        model = self.session.query(ProductModel).filter(
            ProductModel.id == product_id
        ).one_or_none()
        if model == None:
            return None
        
        product = Product(
            model.id,
            self.product_impl,
            Cost(model.rent_or_buy_cost),
            RentalPeriodDuration(timedelta(days=model.standard_rental_period)) if model.standard_rental_period else None
        )
        return product

    def get_product_model_by_id(self, product_id):
        return self.session.query(ProductModel).filter(ProductModel.id == product_id).one_or_none()
    
    def get_product_by_slug(self, slug: str):
        return self.session.query(ProductModel).filter(ProductModel.slug == slug).one_or_none()
    
    def get_all_categories(self):
        return self.session.query(CategoryModel).all()

    def get_product_view_from_model(self, product_model: ProductModel):
        new_cost = self.get_any_cost(product_model.id)
        discount = self.get_discount(product_model.id)

        category = GetCategoryQuery()(self.session, product_model.category_id)
        category_name = category.name if category != None else ""

        items_in_stock = self.get_product_items_count(product_model.id)

        product_view_model = ProductView(
            product_model.id,
            product_model.name,
            product_model.slug,
            product_model.description,
            product_model.image,
            product_model.is_for_rent_or_sale,
            category_name,
            product_model.rent_or_buy_cost,
            new_cost,
            discount,
            product_model.standard_rental_period,
            items_in_stock
        )

        return product_view_model

    def get_products_by_filter(
        self,
        page: int,
        page_size: int = None,
        filter: ProductFilter = None
    ):
        results, total_count = GetProductsQuery()(
            self.session,
            page,
            page_size,
            filter
        )

        products: list[ProductView] = list()
        for row in results:
            product_model, discount_value, new_cost = row.tuple()

            category = GetCategoryQuery()(self.session, product_model.category_id)
            category_name = category.name if category != None else ""

            items_in_stock = self.get_product_items_count(product_model.id)

            product = ProductView(
                product_model.id,
                product_model.name,
                product_model.slug,
                product_model.description,
                product_model.image,
                product_model.is_for_rent_or_sale,
                category_name,
                product_model.rent_or_buy_cost,
                new_cost,
                discount_value,
                product_model.standard_rental_period,
                items_in_stock
            )
            products.append(product)

        return products, total_count
    
    def get_discount(self, product_id):
        discount = Discount.get_from_product(self.discount_impl, product_id)
        if discount == None:
            return 0.0
        return discount.discount_value.amount
    
    def get_initial_cost(self, product_id):
        model = self.session.query(ProductModel).filter(
            ProductModel.id == product_id
        ).one_or_none()

        if model == None:
            return None
        
        return model.rent_or_buy_cost
    
    def get_any_cost(
        self,
        product_id,
        rental_period_duration: timedelta = None,
        quantity: int = 1
    ):
        if product_id == None:
            raise ProductDoesNotExistsError

        if rental_period_duration != None:
            duration = RentalPeriodDuration(rental_period_duration)
        else:
            duration = None
        
        discount = Discount.get_from_product(self.discount_impl, product_id)
        if discount != None:
            cost = discount.get_final_cost(
                Quantity(quantity),
                duration
            )
        else:
            product = self.load_product_domain(product_id)
            if product == None:
                return None
            cost = product.get_final_cost(
                Quantity(quantity),
                duration
            )
        return cost.amount

    def get_cost_for_sale(
        self,
        product_id,
        quantity: int = 1
    ):
        model = self.get_product_model_by_id(product_id)
        if model.is_for_rent_or_sale:
            raise WrongProductTypeError
        return self.get_any_cost(product_id, quantity=quantity)

    def get_cost_for_rent(
        self,
        product_id,
        rental_period_duration: timedelta,
        quantity: int = 1
    ):
        model = self.get_product_model_by_id(product_id)
        if not model.is_for_rent_or_sale:
            raise WrongProductTypeError
        return self.get_any_cost(product_id, rental_period_duration, quantity)
    
    def get_product_items_count(self, product_id):
        return self.item_service.get_product_items_count(product_id)
    
    def get_product_reviews(self, product_id, page: int, page_size: int):
        query = self.session.query(ProductReviewModel).filter(
            ProductReviewModel.product_id == product_id
        )

        total_count = query.count()

        models = query.order_by(
            ProductReviewModel.publication_datetime.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        views = list()
        for model in models:

            user = self.session.query(UserModel).filter(
                UserModel.id == model.user_id
            ).one_or_none()

            view = ProductReviewView(
                model.id,
                model.comment,
                model.score,
                model.publication_datetime,
                user.login
            )
            views.append(view)

        return views, total_count
    
    def get_product_total_score(self, product_id):
        score = self.session.query(func.avg(ProductReviewModel.score)).filter(
            ProductReviewModel.product_id == product_id
        ).one().tuple()[0]

        return score
    
    def post_review(self, user_id, product_id, comment: str, score: int):
        if score < 0 or score > 10:
            raise WrongScoreInReviewError

        if len(comment) > MAX_POST_LEN:
            raise TooManySymbolsInReviewError
        
        model = self.session.query(ProductReviewModel).filter(
            and_(
                ProductReviewModel.user_id == user_id,
                ProductReviewModel.product_id == product_id
            )
        ).one_or_none()

        if model != None:
            raise ReviewAlreadyExistsError

        now = datetime.now(timezone.utc)

        model = ProductReviewModel(
            user_id=user_id,
            product_id=product_id,
            score=score,
            comment=comment,
            publication_datetime=now
        )

        self.session.add(model)
        self.session.flush([model])
    
    def get_xlsx(self, filter: ProductFilter):
        products, _ = self.get_products_by_filter(
            page=1,
            page_size=None,
            filter=filter
        )
        workbook = openpyxl.Workbook()
        ws = workbook.active
        ws.title = "Products"
        ws.append([
            "ID",
            "Название",
            "Категория",
            "Базовая цена",
            "Цена со скидкой",
            "Скидка",
            "В наличии (шт.)"
        ])

        for product in products:
            ws.append([
                product.id,
                product.name,
                product.category,
                product.old_cost,
                product.new_cost,
                f"{product.discount if product.discount > 0.0 else "-"}",
                product.items_in_stock
            ])

        stream = io.BytesIO()
        workbook.save(stream)

        stream.seek(0)
        return stream
