# import time
# from datetime import datetime
# import logging


# _LOGGER = logging.getLogger(__name__)

# UPDATE_INTERVAL = 60
# HEATBOOST_TIMER = 7200
# TEMP_TOLERANCE = 0.3

# class OffsetCalcs:
#     def __init__(self):
#         pass

#     def _set_calculated_offset(self, offsets: dict) -> int:
#         hour = datetime.now().hour
#         if datetime.now().hour < 23 and datetime.now().minute >= 50:
#             hour = datetime.now().hour + 1
#         try:
#             _offset = offsets[hour]
#         except:
#             _LOGGER.warning("No Price-offsets have been calculated. Setting base-offset to 0.")
#             _offset = 0

#         self._current_offset = _offset
#         ret = sum(
#             [
#                 _offset,
#                 self._get_tempdiff_rounded(),
#                 self._get_temp_extremas(),
#                 self._get_temp_trend_offset()
#              ]
#         )

#         #ret = self._add_temp_boost(ret)
#         return int(round(ret, 0))

#     def _add_temp_boost(self, preoffset: int) -> int:
#         if time.time() - self._latest_boost > HEATBOOST_TIMER:
#             if self._hvac.hvac_mode == HvacMode.Idle:
#                 if self._get_tempdiff() < 0:
#                     if self._hvac.hub.sensors.temp_trend_indoors.gradient <= 0.3:
#                         """boost +1 since there is no sunwarming and no heating atm"""
#                         _LOGGER.debug(
#                             "adding additional heating since there is no sunwarming happening and house is too cold.")
#                         preoffset += 1
#                         self._latest_boost = time.time()
#         else:
#             preoffset += 1
#             if self._get_tempdiff() > 1:
#                 """Turn off the boost prematurely"""
#                 preoffset -= 1
#                 self._latest_boost = 0
#         return preoffset

#     def _temporary_lower(self) -> bool:
#         if self._hvac.hub.sensors.peaqev_installed and self._hvac.hvac_mode == HvacMode.Heat:
#             if all([
#                 30 <= datetime.now().minute < 55,
#                 self._hvac.hub.sensors.peaqev_facade.exact_threshold > 100
#             ]):
#                 _LOGGER.debug("Lowering offset because of peak about to be breached.")
#                 return True
#             elif self._hvac.hvac_electrical_addon > 0:
#                 _LOGGER.debug("Lowering offset because electrical addon is on.")
#                 return True
#         return False

#     def max_price_lower(self) -> bool:
#         """Temporarily lower to -10 if this hour is a peak for today and temp > set-temp + 0.5C"""
#         if self._get_tempdiff() >= 0.5:
#             return datetime.now().hour in Offset.peaks_today
#         return False

#     def _get_tempdiff_rounded(self) -> int:
#         """+/- 0.3 C is accepted"""
#         diff = self._get_tempdiff()
#         if diff == 0:
#             return 0
#         return int(diff / TEMP_TOLERANCE)*-1

#     def _get_tempdiff(self) -> float:
#         return self._hvac.hub.sensors.average_temp_indoors.value - self._hvac.hub.sensors.set_temp_indoors.value

#     def _get_temp_trend_offset(self) -> float:
#         if self._hvac.hub.sensors.temp_trend_indoors.is_clean:
#             if self._hvac.hub.sensors.temp_trend_indoors.gradient == 0:
#                 return 0
#             predicted_temp = self._hvac.hub.sensors.average_temp_indoors.value + self._hvac.hub.sensors.temp_trend_indoors.gradient
#             new_temp = predicted_temp - self._hvac.hub.sensors.set_temp_indoors.value
#             if abs(new_temp) >= TEMP_TOLERANCE:
#                 ret = (int(new_temp / TEMP_TOLERANCE) * TEMP_TOLERANCE)*-1
#                 if any([
#                     ret < 0 and self._get_tempdiff_rounded() < 0,
#                     ret > 0 and self._get_tempdiff_rounded() > 0
#                 ]):
#                     return 0
#                 return ret
#         return 0

#     def _get_temp_extremas(self) -> float:
#         set_temp = self._hvac.hub.sensors.set_temp_indoors.value
#         min_diff = abs(set_temp - self._hvac.hub.sensors.average_temp_indoors.min)
#         max_diff = abs(set_temp - self._hvac.hub.sensors.average_temp_indoors.max)

#         if min_diff == max_diff:
#             return 1
#         if max_diff >= min_diff * 2:
#             return -0.5
#         if min_diff >= max_diff * 2:
#             return 0.5
#         return 0