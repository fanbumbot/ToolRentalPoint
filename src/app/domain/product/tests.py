import unittest

from datetime import timedelta, datetime

from .quantity import Quantity, QuantityIsNotPositiveError
from .rental_period import RentalPeriod, RentalPeriodDuration, NegativeDurationError, StartIsGreaterThanEndError

from .cost import Cost
from .product import Product

from ..entity import EntityCQImpl

def get_test_impl():
    impl = EntityCQImpl({})
    return impl

class TestCase(unittest.TestCase):
    def test_quantity_correct(self):
        Quantity(1)

    def test_quantity_wrong(self):
        def sub():
            Quantity(0)
        self.assertRaises(QuantityIsNotPositiveError, sub)

    def test_duration_correct(self):
        RentalPeriodDuration(timedelta(days=1))

    def test_duration_wrong1(self):
        def sub():
            RentalPeriodDuration(timedelta(days=-1))
        self.assertRaises(NegativeDurationError, sub)

    def test_duration_wrong2(self):
        def sub():
            RentalPeriodDuration(-1)
        self.assertRaises(TypeError, sub)

    def test_period_correct(self):
        RentalPeriod(datetime(2025, 1, 1), datetime(2025, 1, 2))

    def test_period_wrong1(self):
        def sub():
            RentalPeriod(datetime(2025, 1, 2), datetime(2025, 1, 1))
        self.assertRaises(StartIsGreaterThanEndError, sub)

    def test_period_wrong2(self):
        def sub():
            RentalPeriod(2025, datetime(2025, 1, 1))
        self.assertRaises(TypeError, sub)

    def test_period_wrong3(self):
        def sub():
            RentalPeriod(datetime(2025, 1, 1), 2025)
        self.assertRaises(TypeError, sub)

    def test_product_create_correct1(self):
        Product.create(
            None,
            get_test_impl(),
            Cost(100),
            RentalPeriodDuration(timedelta(days=10))
        )

    def test_product_create_correct2(self):
        Product.create(
            None,
            get_test_impl(),
            Cost(100),
            None
        )

    def test_product_create_wrong1(self):
        def sub():
            Product.create(
                None,
                get_test_impl(),
                100,
                RentalPeriodDuration(timedelta(days=10))
            )
        self.assertRaises(TypeError, sub)

    def test_product_create_wrong2(self):
        def sub():
            Product.create(
                None,
                get_test_impl(),
                Cost(100),
                10
            )
        self.assertRaises(TypeError, sub)

    def test_product_final_cost_wrong1(self):
        def sub():
            product = Product.create(
                None,
                get_test_impl(),
                100,
                RentalPeriodDuration(timedelta(days=10))
            )

            product.get_final_cost(3, RentalPeriodDuration(timedelta(5)))
        self.assertRaises(TypeError, sub)

    def test_product_final_cost_wrong2(self):
        def sub():
            product = Product.create(
                None,
                get_test_impl(),
                100,
                RentalPeriodDuration(timedelta(days=10))
            )

            product.get_final_cost(Quantity(3), 5)
        self.assertRaises(TypeError, sub)

    def test_product_final_cost_correct1(self):
        product = Product.create(
            None,
            get_test_impl(),
            Cost(100),
            None
        )

        cost = product.get_final_cost(Quantity(3), None).amount
        self.assertEqual(cost, 300)

    def test_product_final_cost_correct2(self):
        product = Product.create(
            None,
            get_test_impl(),
            Cost(100),
            RentalPeriodDuration(timedelta(days=10))
        )

        cost = product.get_final_cost(Quantity(3), RentalPeriodDuration(timedelta(days=3))).amount
        self.assertEqual(cost, 300)
        
    def test_product_final_cost_correct3(self):
        product = Product.create(
            None,
            get_test_impl(),
            Cost(100),
            RentalPeriodDuration(timedelta(days=10))
        )

        cost = product.get_final_cost(Quantity(3), RentalPeriodDuration(timedelta(days=30))).amount
        self.assertEqual(cost, 900)