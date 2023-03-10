# from ...models.chargecontroller_states import ChargeControllerStates
# from .chargecontrollerbase import ChargeControllerBase
# #from custom_components.peaqev.peaqservice.chargecontroller.chargecontrollerbase import ChargeControllerBase


# class ChargeController(ChargeControllerBase):
#     def __init__(self, hub):
#         super().__init__(charger_state_translation=self.self._hub.chargertype.chargerstates)

#     @property
#     def below_startthreshold(self) -> bool:
#         return self._below_start_threshold(
#             predicted_energy=self._hub.prediction.predictedenergy,
#             current_peak=self._hub.current_peak_dynamic,
#             threshold_start=self._hub.threshold.start/100
#         )

#     @property
#     def above_stopthreshold(self) -> bool:
#         return self._above_stop_threshold(
#             predicted_energy=self._hub.prediction.predictedenergy,
#             current_peak=self._hub.current_peak_dynamic,
#             threshold_stop=self._hub.threshold.stop/100
#         )

#     def _get_status_charging(self) -> ChargeControllerStates:
#         if self.above_stopthreshold and self._hub.totalhourlyenergy.value > 0 and self._hub.locale.data.free_charge(self._hub.locale.data) is False:
#             return ChargeControllerStates.Stop
#         else:
#             return ChargeControllerStates.Start

#     def _get_status_connected(self, charger_state=None) -> ChargeControllerStates:
#         if charger_state is not None and self._hub.sensors.carpowersensor.value < 1 and self._is_done(charger_state):
#             return ChargeControllerStates.Done
#         else:
#             if (self.below_startthreshold and self._hub.sensors.totalhourlyenergy.value != 0) or self._hub.sensors.locale.data.free_charge(self._hub.sensors.locale.data) is True:
#                 return ChargeControllerStates.Start
#             else:
#                 return ChargeControllerStates.Stop