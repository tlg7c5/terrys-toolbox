"""Tools for rate limiting."""
import time
from threading import Lock
from typing import List

from terrys_toolbox.exceptions import RateExceededError


class RateLimiter:
    """Thread safe rate limiting using decay.

    Attributes:
        max_calls: The maximum number of calls that can be made within a time period.
        decay_rate: The duration of time in seconds over which to ensure max_calls is not
            exceeded.
    """

    def __init__(self, max_calls: int = 10, decay_rate: float = 1):
        self.max_calls = max_calls
        self.decay_rate = decay_rate
        self.lock = Lock()
        self.calls: List[float] = []

    def _were_decayed_calls(self) -> bool:
        """Remove decayed calls.

        Returns:
            bool indicating whether decayed calls were removed.
        """
        self.calls = [i for i in self.calls if i > time.time()]
        return len(self.calls) < self.max_calls

    def acquire(self, block: bool = True, timeout: int = 0) -> None:
        """Blocking function to enforce a rate limit.

        Args:
            block: Optional bool to indicate whether the function should block
                further processing until a call can be executed without
                breaching the rate limit.  Default is `True`.  If `False`,
                and the rate limit is exceeded, an exception will be raised.
            timeout: Optional number of seconds to block a call.  Default is
                0 or no timeout.  If a timeout is given and a call cannot
                execute within before the expiration of the timeout, an exception
                will be raised after the expiration of the timeout.

        Returns:
            None

        Raises:
            RateExceededError: Raised if a call would execute in violation of the
                rate limit.
        """
        self.lock.acquire()

        if len(self.calls) >= self.max_calls and not self._were_decayed_calls():
            wait_time = self.calls[0] - time.time()
            if (not block) or (timeout and wait_time > timeout):
                self.lock.release()
                time.sleep(timeout)
                raise RateExceededError()
            self.lock.release()
            time.sleep(wait_time)
            self.lock.acquire()

        self.calls.append(time.time() + self.decay_rate)

        self.lock.release()
