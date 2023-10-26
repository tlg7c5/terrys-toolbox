import pytest

from terrys_toolbox.exceptions import RateExceededError
from terrys_toolbox.rate_limiters import RateLimiter


@pytest.mark.parametrize(
    "calls, block, timeout, expected",
    [
        (1, True, 0, {"call_count": 0, "calls": 1}),
        (
            3,
            False,
            0,
            {
                "raises": RateExceededError,
            },
        ),
        (
            3,
            True,
            1,
            {
                "raises": RateExceededError,
                "call_count": 1,
            },
        ),
        (3, True, 0, {"call_count": 1, "calls": 1}),
    ],
    ids=[
        "less than max no sleep",
        "no block raises exception if rate limit exceeded",
        "exception raised if timeout exceeded",
        "sleep called if calls exceed rate limit",
    ],
)
def test_rate_limter_acquire(mocker, calls, block, timeout, expected):
    mock_sleep = mocker.patch("terrys_toolbox.rate_limiters.time.sleep")
    rl = RateLimiter(max_calls=2, decay_rate=2)
    i = 0
    if expected.get("raises", False):
        with pytest.raises(expected["raises"]):
            while i < calls:
                rl.acquire(block=block, timeout=timeout)
                i += 1
        if expected.get("call_count", False):
            assert mock_sleep.call_count == expected["call_count"]
    else:
        while i < calls:
            rl.acquire(block=block, timeout=timeout)
            i += 1
        assert mock_sleep.call_count == expected["call_count"]
