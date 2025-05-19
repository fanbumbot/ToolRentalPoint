import unittest

from datetime import datetime, timedelta

from ..entity import EntityCQImpl

from .period import Period
from .discount_value import DiscountValue
from .discount_season import DiscountSeason, DiscountSeasonAlreadyExistsInThisPeriod

from .implementation.queries.get_discount_by_product import GetDiscountByProductQuery
from .implementation.queries.is_discount_season_belonged import IsDiscountSeasonBelongedQuery
from .implementation.queries.is_product_with_discount import IsProductWithDiscountQuery

from .discount import Discount, Product, ProductAlreadyHasDiscount

from ..product.tests import get_test_impl as get_product_test_impl
from ..product.cost import Cost
from ..product.quantity import Quantity

class GetDiscountByProductQueryImpl(GetDiscountByProductQuery):
    def __init__(self, all_discounts: dict[int, Discount]):
        self.all_discounts = all_discounts

    def __call__(self, product_id):
        discount = self.all_discounts[product_id]
        return discount

class IsProductWithDiscountQueryImpl(IsProductWithDiscountQuery):
    def __init__(self, all_discounts: dict[int, Discount]):
        self.all_discounts = all_discounts

    def __call__(self, product: Product):
        return product.id in self.all_discounts

class IsDiscountSeasonBelongedQueryImpl(IsDiscountSeasonBelongedQuery):
    def __init__(self, all_discount_seasons: list[DiscountSeason]):
        self.all_discount_seasons = all_discount_seasons

    def __call__(self, period: Period):
        for season in self.all_discount_seasons:
            if (
                (season.period.start_datetime <= period.start_datetime and
                season.period.end_datetime >= period.start_datetime) or
                (season.period.start_datetime <= period.end_datetime and
                season.period.end_datetime >= period.end_datetime)
            ):
                return True
        return False

def get_discount_season_test_impl(all_discount_seasons):
    impl = EntityCQImpl({
        IsDiscountSeasonBelongedQuery: IsDiscountSeasonBelongedQueryImpl(all_discount_seasons)
    })
    return impl

def get_discount_test_impl(all_discounts):
    impl = EntityCQImpl({
        GetDiscountByProductQuery: GetDiscountByProductQueryImpl(all_discounts),
        IsProductWithDiscountQuery: IsProductWithDiscountQueryImpl(all_discounts)
    })
    return impl

class TestCase(unittest.TestCase):
    all_discount_seasons = list()
    all_discounts = dict()

    def test_period_correct1(self):
        Period(datetime(2025, 1, 1), datetime(2025, 1, 2))

    def test_period_correct2(self):
        Period(datetime(2025, 1, 1), datetime(2025, 1, 1))

    def test_period_wrong1(self):
        def sub():
            Period(datetime(2025, 1, 2), datetime(2025, 1, 1))

        self.assertRaises(ValueError, sub)

    def test_period_wrong2(self):
        def sub():
            Period(datetime(2025, 1, 2), 222)

        self.assertRaises(TypeError, sub)

    def test_period_wrong3(self):
        def sub():
            Period(222, datetime(2025, 1, 2))

        self.assertRaises(TypeError, sub)

    def test_discount_value_correct(self):
        DiscountValue(0.7)

    def test_discount_value_wrong2(self):
        def sub():
            DiscountValue("abc")

        self.assertRaises(TypeError, sub)

    def test_discount_value_wrong3(self):
        def sub():
            DiscountValue(1.2)

        self.assertRaises(ValueError, sub)

    def test_discount_value_wrong4(self):
        def sub():
            DiscountValue(-0.1)

        self.assertRaises(ValueError, sub)

    def test_discount_season_create_correct(self):
        DiscountSeason.create(
            None,
            get_discount_season_test_impl(self.__class__.all_discount_seasons),
            Period(datetime(2025, 1, 1), datetime(2025, 1, 2))
        )

    def test_discount_season_create_wrong1(self):
        def sub():
            DiscountSeason.create(
                None,
                get_discount_season_test_impl(self.__class__.all_discount_seasons),
                None
            )
        self.assertRaises(TypeError, sub)

    def test_discount_season_create_wrong2(self):
        def sub():
            self.__class__.all_discount_seasons.clear()
            season = DiscountSeason.create(
                None,
                get_discount_season_test_impl(self.__class__.all_discount_seasons),
                Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
            )
            self.__class__.all_discount_seasons.append(season)
            DiscountSeason.create(
                None,
                get_discount_season_test_impl(self.__class__.all_discount_seasons),
                Period(datetime(2025, 1, 5), datetime(2025, 1, 7))
            )
        self.assertRaises(DiscountSeasonAlreadyExistsInThisPeriod, sub)

    def test_discount_create_correct(self):
        product = Product(
            None,
            get_product_test_impl(),
            Cost(100),
            None
        )
        Discount.create(
            None,
            get_discount_test_impl(self.__class__.all_discounts),
            product,
            DiscountValue(0.5),
            DiscountSeason(
                None,
                get_discount_season_test_impl(self.__class__.all_discount_seasons),
                Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
            )
        )

    def test_discount_create_wrong1(self):
        def sub():
            Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                100,
                DiscountValue(0.5),
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )
        self.assertRaises(TypeError, sub)

    def test_discount_create_wrong2(self):
        def sub():
            product = Product(
                None,
                get_product_test_impl(),
                Cost(100),
                None
            )
            Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                0.5,
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )
        self.assertRaises(TypeError, sub)

    def test_discount_create_wrong3(self):
        def sub():
            product = Product(
                None,
                get_product_test_impl(),
                Cost(100),
                None
            )
            Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                DiscountValue(0.5),
                None
            )
        self.assertRaises(TypeError, sub)

    def test_discount_create_wrong4(self):
        def sub():
            product = Product(
                1,
                get_product_test_impl(),
                Cost(100),
                None
            )
            discount = Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                DiscountValue(0.5),
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )
            self.__class__.all_discounts[product.id] = discount

            Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                DiscountValue(0.5),
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )
        self.assertRaises(ProductAlreadyHasDiscount, sub)

    def test_get_final_cost_correct(self):
        product = Product(
            1,
            get_product_test_impl(),
            Cost(100),
            None
        )
        discount = Discount.create(
            None,
            get_discount_test_impl(self.__class__.all_discounts),
            product,
            DiscountValue(0.5),
            DiscountSeason(
                None,
                get_discount_season_test_impl(self.__class__.all_discount_seasons),
                Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
            )
        )

        cost = discount.get_final_cost(
            Quantity(4),
            None
        )

        self.assertEqual(cost.amount, 200)

    def test_get_final_cost_wrong1(self):
        def sub():
            product = Product(
                1,
                get_product_test_impl(),
                Cost(100),
                None
            )
            discount = Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                DiscountValue(0.5),
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )

            discount.get_final_cost(
                4,
                None
            )

        self.assertRaises(TypeError, sub)

    def test_get_final_cost_wrong2(self):
        def sub():
            product = Product(
                1,
                get_product_test_impl(),
                Cost(100),
                None
            )
            discount = Discount.create(
                None,
                get_discount_test_impl(self.__class__.all_discounts),
                product,
                DiscountValue(0.5),
                DiscountSeason(
                    None,
                    get_discount_season_test_impl(self.__class__.all_discount_seasons),
                    Period(datetime(2025, 1, 1), datetime(2025, 1, 10))
                )
            )

            discount.get_final_cost(
                Quantity(4),
                timedelta(days=4)
            )

        self.assertRaises(TypeError, sub)