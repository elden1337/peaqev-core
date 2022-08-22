import pytest
from ..hub.hub import Hub
from ..hub.hub_options import HubOptions, Price
from ..models.hourselection.const import (CAUTIONHOURTYPE_AGGRESSIVE, CAUTIONHOURTYPE_INTERMEDIATE, CAUTIONHOURTYPE_SUAVE, CAUTIONHOURTYPE)
from ..services.locale.Locale import LOCALE_SE_GOTHENBURG

OPTIONS_REGULAR = HubOptions(
    price=Price(
        price_aware=True,
        allow_top_up=False,
        cautionhour_type=CAUTIONHOURTYPE_SUAVE
    ),
    peaqev_lite=False,
    startpeaks={1:2, 2:2, 3:1.8, 4:1.5, 5:1.5, 6:1.5, 7:1.5, 8:1.5, 9:1.5, 10:1.8, 11:2, 12:2}
)
OPTIONS_REGULAR.locale = LOCALE_SE_GOTHENBURG

MOCK_CHARGER_OBJ = ""
MOCK_STATE_MACHINE = ""


def test_hub_init():
    h = Hub(options=OPTIONS_REGULAR,domain="test", state_machine=MOCK_STATE_MACHINE, chargerobj = MOCK_CHARGER_OBJ, is_test=True)
    assert h.domain == "test"