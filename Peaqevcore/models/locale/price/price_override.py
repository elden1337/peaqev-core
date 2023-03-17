from .locale_price import LocalePrice
from datetime import datetime, timedelta

#mock
from peaqevcore.services.locale.countries.sweden import SE_Gothenburg
AVG_PRICE_SEVEN_DAYS = 2.59
PRICES = [1.715, 1.665, 1.138, 1.112, 1.019, 0.925, 0.925, 0.937, 1.499, 1.7, 1.708, 1.678, 1.339, 0.925, 0.593, 0.485, 0.416, 0.412, 0.412, 0.41, 0.404, 0.409, 0.362, 0.306, 0.282, 0.198] #0 is current hour.
#mock

class PriceOverride:
    """When to override peaks"""
    peak_peak = 10

    def __init__(self, price:LocalePrice) -> None:
        self._price_type = price.price_type
        self._cost = price.value

    #if tiered price we should obv allow up to just below the next level.

    @property
    def increase(self) -> float:
        prices = PRICES #get from nordpool-data
        avg = AVG_PRICE_SEVEN_DAYS #get from sensor
        if prices[0] >= (avg*0.75):
            return 0.0

        period = self._rest_of_period()
        return self._calculate_increase(period_len=period, avg_price=avg, prices=prices)

    def _calculate_increase(self, period_len, avg_price, prices:list) -> float:
        addition = 0
        price_determination = self._calc_price_determinator(
            current_price=prices[0], 
            avg_price=avg_price, 
            prognosis=prices[1::]
            )
        try:
            while (addition * self._cost)/period_len < price_determination:
                addition += 0.1
        except ZeroDivisionError:
            pass
        return round(addition,1)

    @staticmethod
    def _calc_price_determinator(current_price:float, avg_price:float, prognosis:list) -> float:
        #dont forget to handle if price is 0 or lower.
        return 5
        
    @staticmethod
    def _rest_of_period() -> int:
        today: datetime = datetime.now().date()
        next_month = today.replace(day=28) + timedelta(days=4)
        ret: datetime = next_month - timedelta(days=next_month.day)
        return ret.day-today.day
    


# i = PriceOverride(cost=SE_Gothenburg.price)
# print(i.increase)
