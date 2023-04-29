from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..hoursselection import Hoursselection

import logging
from datetime import datetime
from typing import Tuple
import statistics as stat

from .hoursselection_helpers import async_create_dict
from .hourselection_calculations import (
    async_normalize_prices,
    async_create_cautions,
    async_get_offset_dict,
    async_should_be_cautionhour,
    async_set_charge_allowance,
)
from ....models.hourselection.hourobjects.hourobject import HourObject
from ....models.hourselection.hourobjects.hourobject_helpers import (
    async_update_interim_lists,
)
from ....models.hourselection.day_types import DayTypes

_LOGGER = logging.getLogger(__name__)


class HourSelectionService:
    def __init__(self, parent: Hoursselection, base_mock_hour: int | None = None):
        self.parent = parent
        self._mock_hour = base_mock_hour
        self._mock_day: int | None = None
        self.preserve_interim: bool = False
        self._midnight_touched: bool = False

    async def async_update(self) -> None:
        if all(
            [
                len(self.parent.model.prices_today) == 0,
                len(self.parent.model.prices_tomorrow) == 0,
            ]
        ):
            return
        if self.preserve_interim:
            await self.async_change_midnight_data()
        else:
            self._midnight_touched = False
            today = await self.async_update_per_day(
                prices=self.parent.model.prices_today, day_type=DayTypes.Today
            )
            tomorrow = await self.async_update_per_day(
                prices=self.parent.model.prices_tomorrow, day_type=DayTypes.Tomorrow
            )
            hours, hours_tomorrow = await self.async_interim_day_update(today, tomorrow)

            self.parent.model.hours.hours_today = (
                await self.async_add_remove_limited_hours(
                    hours, day_type=DayTypes.Today
                )
            )
            self.parent.model.hours.hours_tomorrow = (
                await self.async_add_remove_limited_hours(
                    hours_tomorrow, day_type=DayTypes.Tomorrow
                )
            )
            hour = await self.async_set_hour()
            await self.parent.model.hours.async_update_hour_lists(hour=hour)

    async def async_change_midnight_data(self) -> None:
        if self.parent.model.prices_tomorrow == []:
            if not self._midnight_touched:
                self._midnight_touched = (
                    await self.parent.model.hours.async_touch_midnight()
                )
        else:
            self.preserve_interim = False
            await self.async_update()

    async def async_update_per_day(
        self, prices: list, day_type: DayTypes, range_start: int = 0
    ) -> HourObject:
        _LOGGER.debug(f"Updating {day_type.name}")
        pricedict = {}
        if prices is not None and len(prices) > 1:
            pricedict = await async_create_dict(prices)
            normalized_pricedict = await async_create_dict(
                await async_normalize_prices(prices)
            )
            if stat.stdev(prices) > 0.05:
                ranked = await async_create_cautions(
                    pricedict,
                    normalized_pricedict,
                    self.parent.cautionhour_type_enum,
                    range_start,
                    self.parent.model.adjusted_average,
                    self.parent.model.options.blocknocturnal,
                )
                ready_hours = await self.async_determine_hours(ranked, prices)
                ret = HourObject(
                    nh=ready_hours.nh,
                    ch=ready_hours.ch,
                    dyn_ch=ready_hours.dyn_ch,
                    pricedict=pricedict,
                )
            else:
                """the price curve is too flat to determine hours"""
                ret = HourObject(nh=[], ch=[], dyn_ch={}, pricedict=pricedict)
            ret.offset_dict = await async_get_offset_dict(normalized_pricedict)
            return ret
        return HourObject([], [], {})

    async def async_add_remove_limited_hours(
        self, hours: HourObject, day_type: DayTypes
    ) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None or all(
            [len(hours.nh) == 0, len(hours.ch) == 0, len(hours.dyn_ch) == 0]
        ):
            return HourObject(offset_dict=hours.offset_dict, pricedict=hours.pricedict)
        match day_type:
            case DayTypes.Today | DayTypes.Interim:
                await hours.async_add_expensive_hours(
                    self.parent.model.options.absolute_top_price
                )
            case DayTypes.Tomorrow:
                _top = await self.parent.model.options.async_add_tomorrow_to_top_price(
                    self.parent.prices_tomorrow, self._mock_day
                )
                await hours.async_add_expensive_hours(_top)
        return await hours.async_remove_cheap_hours(self.parent.model.options.min_price)

    async def async_determine_hours(self, price_list: dict, prices: list) -> HourObject:
        ret = HourObject([], [], {})
        try:
            for p in price_list:
                if price_list[p]["force_non"] is True:
                    ret.nh.append(p)
                elif await async_should_be_cautionhour(
                    price_list[p],
                    prices,
                    self.parent.model.current_peak,
                    self.parent.model.options.cautionhour_type,
                ):
                    ret.ch.append(p)
                    ret.dyn_ch[p] = round(
                        await async_set_charge_allowance(
                            price_list[p]["permax"],
                            self.parent.model.options.cautionhour_type,
                        ),
                        2,
                    )
                else:
                    ret.nh.append(p)
        except IndexError as e:
            _LOGGER.error(f"Error in determine hours: {e}")
        return ret

    async def async_interim_day_update(
        self, today: HourObject, tomorrow: HourObject
    ) -> Tuple[HourObject, HourObject]:
        """Updates the non- and caution-hours with an adjusted mean of 14h - 13h today-tomorrow to get a more sane nightly curve."""
        if len(self.parent.model.prices_tomorrow) < 23:
            self.preserve_interim = False
            return today, tomorrow

        hour = await self.async_set_hour()
        # hour = len(self.parent.prices) - 10
        # negative_hour = hour * -1
        negative_hour = (len(self.parent.prices) - hour) * -1
        print(hour)
        print(negative_hour)
        pricelist = self.parent.model.prices_today[hour::]
        pricelist[len(pricelist) :] = self.parent.model.prices_tomorrow[0:hour]
        new_hours = await self.async_update_per_day(
            prices=pricelist, range_start=hour, day_type=DayTypes.Interim
        )

        today = await async_update_interim_lists(
            range(hour, len(self.parent.prices)), today, new_hours, hour
        )
        tomorrow = await async_update_interim_lists(
            range(0, hour), tomorrow, new_hours, negative_hour
        )
        self.preserve_interim = True
        return today, tomorrow

    # helpers
    def set_hour(self, testhour: int | None = None) -> int:
        return (
            testhour
            if testhour is not None
            else self._mock_hour
            if self._mock_hour is not None
            else datetime.now().hour
        )

    async def async_set_hour(self, testhour: int | None = None) -> int:
        return (
            testhour
            if testhour is not None
            else self._mock_hour
            if self._mock_hour is not None
            else datetime.now().hour
        )

    async def async_set_day(self, day: int | None = None):
        self._mock_day = day if day is not None else datetime.now().day
