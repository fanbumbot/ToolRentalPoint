from abc import ABC

class GetDiscountByProductQuery(ABC):
    def __call__(self, product_id):
        pass