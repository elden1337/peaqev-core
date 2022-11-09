from enum import Enum

class CHARGERSTATES(Enum):
    Idle = "Idle"
    Connected = "Connected"
    Start = "Start"
    Stop = "Stop"
    Done = "Done"
    Error = "Error, check logs."
    Charging = "Charging"
    Disabled = "Disabled"
