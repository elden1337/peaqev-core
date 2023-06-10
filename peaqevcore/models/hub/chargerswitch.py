import logging
from .hubmember import HubMember

_LOGGER = logging.getLogger(__name__)


class ChargerSwitch(HubMember):
    def __init__(
        self,
        hass,
        data_type: type,
        listenerentity,
        initval,
        # currentname: str,
        hubdata=None,
        init_override: bool = False,
    ):
        self._hubdata = hubdata
        self._hass = hass
        self._value = initval

        super().__init__(
            data_type=data_type,
            listenerentity=listenerentity,
            init_override=init_override,
            initval=initval,
            hass=hass,
        )

    @property
    def is_initialized(self) -> bool:
        if (
            self._hubdata.chargerobject is not None
            and not self._hubdata.chargerobject.is_initialized
        ):
            return False
        return super().is_initialized

    HASLOGGED_INITWARN = False

    async def async_log_warning_once(self):
        if not self.HASLOGGED_INITWARN:
            _LOGGER.warning(
                "Chargerobject state was None while getting current. "
                "Updatecurrent will still process but you may see a missmatch in frontend."
            )
            self.HASLOGGED_INITWARN = True
