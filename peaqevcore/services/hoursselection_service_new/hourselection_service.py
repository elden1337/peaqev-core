from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.list_type import ListType
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean
from datetime import date, datetime, time
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices
from .offset_dict import get_offset_dict, set_offset_dict
from .permittance import set_initial_permittance, set_scooped_permittance
from .max_min_charge import MaxMinCharge


class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)
        self._offset_dict: dict[datetime, dict] = {}

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
        ret = [hp for hp in self.model.hours_prices if not hp.passed]
        if self.max_min.active:
            for r in ret:
                if r in self.max_min.non_hours:
                    r.permittance = 0.0
                elif r.dt in self.max_min.dynamic_caution_hours.keys():
                    r.permittance = self.max_min.dynamic_caution_hours[r.dt]
        return ret

    @property
    def passed_hours(self) -> list[HourPrice]:
        self.update()
        return [hp for hp in self.model.hours_prices if hp.passed]

    @property
    def stopped_string(self) -> str:
        self.update()
        return self.allowance.display_name

    @property
    def allowance(self) -> AllowanceObj:
        return set_allowance_obj(self.dtmodel, self.future_hours)

    @property
    def average_kwh_price(self) -> float:
        try:
            return round(
                mean(
                    [
                        hp.permittance * hp.price
                        for hp in self.future_hours
                        if hp.permittance > 0
                    ]
                ),
                2,
            )
        except Exception:
            return 0.0

    @property
    def offset_dict(self) -> dict:
        return get_offset_dict(self._offset_dict)

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if self._do_recalculate_prices(prices, prices_tomorrow):
            self.model.hours_prices = await self.async_create_prices(
                prices, prices_tomorrow
            )

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            await self.async_set_permittance(self.model.hours_prices)

    def _do_recalculate_prices(self, prices, prices_tomorrow) -> bool:
        if [
            hp.price
            for hp in self.model.hours_prices
            if hp.dt.date() == self.dtmodel.hdate
        ] == prices and len(prices_tomorrow) < 1:
            return False
        return True

    async def async_create_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        # todo: fix to allow 23, 24,25, 92, 96, 100 for dst-dates.
        match len(prices):
            case 23 | 24 | 25:
                return await self.async_create_hour_prices(
                    prices, prices_tomorrow, False
                )
            case 92 | 96 | 100:
                return await self.async_create_hour_prices(
                    prices, prices_tomorrow, True
                )
            case 0:
                return []
        raise ValueError(
            f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
        )

    async def async_create_hour_prices(
        self,
        prices: list[float],
        prices_tomorrow: list[float] = [],
        is_quarterly: bool = False,
    ) -> list:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        ret = []
        ret.extend(self._set_hourprice_list(prices, is_quarterly, self.dtmodel.hdate))
        ret.extend(
            self._set_hourprice_list(
                prices_tomorrow, is_quarterly, self.dtmodel.hdate_tomorrow
            )
        )
        return await self.async_set_permittance(ret)

    def _set_hourprice_list(
        self, prices: list, is_quarterly: bool, datum: date
    ) -> list[HourPrice]:
        ret = []
        for idx, p in enumerate(prices):  # type: ignore
            assert isinstance(p, (float, int))
            hour = int(idx / 4) if is_quarterly else idx
            quarter = idx % 4 if is_quarterly else 0
            _dt = datetime.combine(
                datum, time(hour=hour, minute=quarter * 15, second=0, microsecond=0)
            )
            ret.append(
                HourPrice(
                    dt=_dt,
                    # day=datum,
                    # hour=hour,
                    quarter=quarter,
                    price=p,
                    passed=self.dtmodel.is_passed(datum, hour, quarter),
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                    list_type=ListType.Quarterly if is_quarterly else ListType.Hourly,
                )
            )
        return ret

    async def async_set_permittance(
        self, hour_prices: list[HourPrice]
    ) -> list[HourPrice]:
        prices = normalize_prices([hp.price for hp in hour_prices])
        set_initial_permittance(
            hour_prices,
            mean(prices),
            stdev(prices),
            self.model.adjusted_average,
        )
        set_scooped_permittance(
            hour_prices,
            self.options.cautionhour_type_enum,
        )
        self._offset_dict = set_offset_dict(prices, hour_prices[0].dt.date())
        self._block_nocturnal(hour_prices, self.options.blocknocturnal)
        return hour_prices

    @staticmethod
    def _block_nocturnal(
        hour_prices: list[HourPrice], block_nocturnal: bool = False
    ) -> None:
        blockhours = [23, 0, 1, 2, 3, 4, 5, 6]
        if block_nocturnal:
            for hp in hour_prices:
                if hp.hour in blockhours:
                    hp.permittance = 0.0
