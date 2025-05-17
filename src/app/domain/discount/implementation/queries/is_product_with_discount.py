from abc import ABC

from ....product.product import Product

class IsProductWithDiscountQuery(ABC):
    def __call__(self, product: Product) -> bool:
        pass