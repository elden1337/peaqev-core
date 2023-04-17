from dataclasses import dataclass, field


@dataclass
class HourObject:
    nh: list = field(default_factory=lambda: [])
    ch: list = field(default_factory=lambda: [])
    dyn_ch: dict = field(default_factory=lambda: {})
    offset_dict: dict = field(default_factory=lambda: {})
    pricedict: dict = field(default_factory=lambda: {})

    async def async_remove_cheap_hours(self, min_price:float = 0):
        lst = (h for h in self.pricedict if self.pricedict[h] < min_price)
        for h in lst:
            if h in self.nh:
                self.nh.remove(h)
            elif h in self.ch:
                self.ch.remove(h)
                self.dyn_ch.pop(h)    
        return self

    async def async_add(self, lst: list):
        for h in lst:
            if h not in self.nh:
                self.nh.append(h)
                if h in self.ch:
                    self.ch.remove(h)
                if len(self.dyn_ch):
                    if h in self.dyn_ch.keys():
                        self.dyn_ch.pop(h)

    async def async_add_expensive_hours(self, max_price: float = 0):
        lst = (h for h in self.pricedict if self.pricedict[h] >= max_price)
        await self.async_add(lst)
        self.nh.sort()
        return self
