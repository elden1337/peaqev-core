from dataclasses import dataclass
from datetime import datetime

@dataclass
class PrognosisExportModel:
  prognosis_temp: float
  corrected_temp: float
  windchill_temp: float
  DT: datetime
  TimeDelta: int