from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean
from datetime import datetime, timedelta
from ...models.hourselection.hourselection_options import HourSelectionOptions
from ...models.hourselection.cautionhourtype import CautionHourType
from .models.hour_type import HourType


class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionModel()

    def update(self):
        for hp in self.model.hours_prices:
            hp.set_passed(self.dtmodel)

    async def async_update(self):
        self.update()

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        return [hp for hp in self.model.hours_prices if not hp.passed]

    @property
    def passed_hours(self) -> list[HourPrice]:
        self.update()
        return [hp for hp in self.model.hours_prices if hp.passed]

    @property
    def stopped_string(self) -> str:
        return self.allowance.display_name
    
    @property
    def allowance(self) -> AllowanceObj:
        return set_allowance_obj(self.dtmodel, self.future_hours)
    
    @property
    def non_hours(self) -> list[datetime]:
        return [
            hp.dt
            for hp in self.model.hours_prices
            if not hp.passed and hp.permittance == 0.0
        ]

    @property
    def caution_hours(self) -> list[datetime]:
        return list(self.dynamic_caution_hours.keys())

    @property
    def dynamic_caution_hours(self) -> dict[datetime, float]:
        return {
            hp.dt: hp.permittance
            for hp in self.model.hours_prices
            if not hp.passed and 0.0 < hp.permittance < 1.0
        }

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if self._do_recalculate_prices(prices):
            self.model.hours_prices = await self.async_create_hour_prices(
                prices, prices_tomorrow
            )

    def _do_recalculate_prices(self, prices) -> bool:
        if [
            hp.price for hp in self.model.hours_prices if hp.day == self.dtmodel.hdate
        ] == prices:
            return False
        return True

    async def async_create_hour_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        match len(prices):
            case 24:
                return await self.async_create_hour_prices_hourly(
                    prices, prices_tomorrow
                )
            case 96:
                return self._create_hour_prices_quarterly(prices, prices_tomorrow)
            case 0:
                return []
        raise ValueError(f"Prices must be either 24 or 96. len is {len(prices)}")

    def _create_hour_prices_quarterly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        return []

    async def async_create_hour_prices_hourly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        ret = []
        for idx, p in enumerate(prices):
            assert isinstance(p, (float, int))
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate,
                    hour=idx,
                    price=p,
                    passed=True if idx < self.dtmodel.hour else False,
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        for idx, p in enumerate(prices_tomorrow):
            assert isinstance(p, float)
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate_tomorrow,
                    hour=idx,
                    price=p,
                    passed=False,
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        await self.async_set_permittance(ret)
        return ret

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            await self.async_set_permittance(self.model.hours_prices)

    async def async_set_permittance(self, hour_prices: list[HourPrice]) -> None:
        prices = [hp.price for hp in hour_prices]
        price_mean = self._set_price_mean(prices, self.model.adjusted_average)
        price_stdev = stdev(prices)
        self._set_initial_permittance(hour_prices, price_mean, price_stdev)
        self._set_scooped_permittance(hour_prices, self.options.cautionhour_type_enum)

    @staticmethod
    def _set_price_mean(prices: list[float], adjusted_average: float | None) -> float:
        #print(f"adj: {adjusted_average}")
        if not adjusted_average:
            return mean(prices)
        return mean([adjusted_average, mean(prices)])

    @staticmethod
    def _set_initial_permittance(
        hour_prices: list[HourPrice], price_mean: float, price_stdev: float
    ) -> None:
        # print(f"price_mean: {price_mean}")
        # print(f"price_stdev: {price_stdev}")
        for hp in hour_prices:
            if hp.hour_type == HourType.BelowMin:
                hp.permittance = 1.0
            elif hp.hour_type == HourType.AboveMax:
                hp.permittance = 0.0
            elif hp.price < price_mean - price_stdev:
                hp.permittance = 1.0
            elif hp.price > price_mean + price_stdev:
                hp.permittance = 0.0
            else:
                hp.permittance = round(
                    1.0 - ((hp.price - price_mean + price_stdev) / (2 * price_stdev)), 2
                )

    @staticmethod
    def _set_scooped_permittance(
        hour_prices: list[HourPrice], caution_hour_type: CautionHourType
    ) -> None:
        lo_cutoff = 0.5
        hi_cutoff = 0.75
        max_hours = 24  # todo: add support for 96 if quarterly
        match caution_hour_type:
            case CautionHourType.SUAVE:
                hi_cutoff = 0.7
            case CautionHourType.INTERMEDIATE:
                lo_cutoff = 0.6
                hi_cutoff = 0.7
            case CautionHourType.AGGRESSIVE:
                lo_cutoff = 0.7
            case CautionHourType.SCROOGE:
                lo_cutoff = 0.7
                max_hours = 8  # todo: add support for 32 if quarterly

        for i in hour_prices:
            _t = i.permittance
            if i.permittance <= lo_cutoff:
                i.permittance = 0.0
            elif i.permittance >= hi_cutoff:
                i.permittance = 1.0

    def _sort_hour_prices(self, hour_prices: list[HourPrice]) -> list[HourPrice]:
        sorted_hour_prices = sorted(
            hour_prices, key=lambda hp: (hp.day, hp.hour, hp.quarter)
        )
        return sorted_hour_prices


# #-----------------main.py
# import asyncio

# P230520 = [
#     [
#         0.22,
#         0.17,
#         0.15,
#         0.16,
#         0.1,
#         0.1,
#         0.11,
#         0.14,
#         0.15,
#         0.15,
#         0.14,
#         0.08,
#         0.08,
#         0.07,
#         0.08,
#         0.08,
#         0.1,
#         0.17,
#         0.65,
#         0.74,
#         0.62,
#         0.17,
#         0.11,
#         0.09,
#     ],
#     [
#         0.08,
#         0.08,
#         0.08,
#         0.08,
#         0.08,
#         0.08,
#         0.1,
#         0.12,
#         0.13,
#         0.11,
#         0.08,
#         0.07,
#         0.02,
#         0.01,
#         0.02,
#         0.03,
#         0.07,
#         0.11,
#         0.67,
#         1.07,
#         1.15,
#         1.08,
#         0.64,
#         0.13,
#     ],
# ]

# import matplotlib.pyplot as plt

# def graph_hour_prices(hour_prices: list[HourPrice]) -> None:
#     # Extract the prices and quarters from the HourPrice objects
#     permittance = [hp.permittance for hp in hour_prices]
#     idx = [hp.idx for hp in hour_prices]

#     # Create a line plot of the prices vs. quarters
#     plt.plot(idx, permittance)
#     plt.xlabel('Quarter')
#     plt.ylabel('Price')
#     plt.title('Hour Prices')
#     plt.show()

# async def do():
#     opt = HourSelectionOptions(max_price=2, min_price=0.05, caution_hour_type=1)
#     hss = HourSelectionService(opt)
#     await hss.async_update_prices(P230520[0], P230520[1])
#     # for p in hss.model.hours_prices:
#     #     print(p)
#     #graph_hour_prices(hss.model.hours_prices)

#     print(hss.non_hours)
#     print(hss.dynamic_caution_hours)
#     # print("---- updating date")
#     # hss.dtmodel.set_date(date(2023, 5, 24))
#     # await hss.async_update()
#     # for p in hss.model.hours_prices:
#     #     print(p)


#     # print(list(map(lambda x: x.quarter, hss.model.hours_prices)))
#     # filtered_list = list(
#     #     filter(lambda obj: obj.hour_type == HourType.BelowMin, hss.model.hours_prices)
#     # )
#     # for f in filtered_list:
#     #     print(f)


# if __name__ == "__main__":
#     asyncio.run(do())
