import time

class WaitTimer:
    def __init__(self, timeout: int, init_now: bool = True):
        self._timeout = timeout
        self._base_timeout = timeout
        self._last_update = time.time() if init_now else 0

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def value(self) -> float:
        return self._last_update

    def update(self, override=None) -> None:
        if override is not None:
            self._timeout = override
        self._last_update = time.time()

    def reset(self) -> None:
        self._last_update = 0
        self._timeout = self._base_timeout

    def is_timeout(self) -> bool:
        if self._timeout == 0:
            return False
        if time.time() - self._last_update > self._timeout:
            self._last_update = time.time()
            self._timeout = self._base_timeout
            return True
        return False
    

boost_wait = WaitTimer(timeout=300, init_now=False)
print(boost_wait.is_timeout())
boost_wait.update()
print(boost_wait.is_timeout())
