from ...usecase.service.discount_season import DiscountSeasonService

def get_discount_season_service(session):
    discount_season_service = DiscountSeasonService(session)
    return discount_season_service