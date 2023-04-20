from .savings_model import SavingsModel

class SavingsService:
    def __init__(self, peak_price: float) -> None:
        self.model = SavingsModel(peak_price)

    @property
    def savings_peak(self) -> float:
        return 0
    
    @property
    def savings_trade(self) -> float:
        return 0
    
    @property
    def savings_total(self) -> float:
        return sum([self.savings_peak, self.savings_trade])
    
