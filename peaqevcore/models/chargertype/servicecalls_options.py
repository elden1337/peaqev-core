from dataclasses import dataclass

@dataclass
class ServiceCallsOptions:
    allowupdatecurrent: bool
    update_current_on_termination: bool
    switch_controls_charger: bool = False
    """
    This is for outlet control. 
    If false we call services to enable/disable. 
    If true we call a switch
    """