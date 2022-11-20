from dataclasses import dataclass, field

@dataclass
class HourObject:
    nh: list
    ch: list
    dyn_ch: dict
    offset_dict: dict = field(default_factory=lambda: {})
    pricedict: dict = field(default_factory=lambda: {})

    def remove_cheap_hours(self, min_price:float = 0):
        lst = (h for h in self.pricedict if self.pricedict[h] < min_price)
        for h in lst:
            if h in self.nh:
                self.nh.remove(h)
            elif h in self.ch:
                self.ch.remove(h)
                self.dyn_ch.pop(h)    
        return HourObject(nh=self.nh, ch=self.ch, dyn_ch=self.dyn_ch, offset_dict=self.offset_dict)

    def add_expensive_hours(self, max_price: float = 0):
        lst = (h for h in self.pricedict if self.pricedict[h] >= max_price)
        for h in lst:
            if h not in self.nh:
                self.nh.append(h)
                if h in self.ch:
                    self.ch.remove(h)
                if len(self.dyn_ch) > 0:
                    if h in self.dyn_ch.keys():
                        self.dyn_ch.pop(h)
        self.nh.sort()
        return HourObject(nh=self.nh, ch=self.ch, dyn_ch=self.dyn_ch, offset_dict=self.offset_dict)

# @dataclass
# class HourObjectExtended(HourObject):
#     pricedict: dict = field(default_factory=lambda: {})

#     def remove_cheap_hours(self, min_price:float = 0) -> HourObject:
#             lst = (h for h in self.pricedict if self.pricedict[h] < min_price)
#             for h in lst:
#                 if h in self.nh:
#                     self.nh.remove(h)
#                 elif h in self.ch:
#                     self.ch.remove(h)
#                     self.dyn_ch.pop(h)    
#             return HourObject(self.nh, self.ch, self.dyn_ch)

#     def add_expensive_hours(self, max_price: float = 0) -> HourObject:
#         lst = (h for h in self.pricedict if self.pricedict[h] >= max_price)
#         for h in lst:
#             if h not in self.nh:
#                 self.nh.append(h)
#                 if h in self.ch:
#                     self.ch.remove(h)
#                 if len(self.dyn_ch) > 0:
#                     if h in self.dyn_ch.keys():
#                         self.dyn_ch.pop(h)
#         self.nh.sort()
#         return HourObject(self.nh, self.ch, self.dyn_ch)