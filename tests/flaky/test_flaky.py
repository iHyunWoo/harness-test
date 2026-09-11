"""의도적으로 불안정한 테스트.

Harness의 flaky test 탐지와 테스트 리포트를 확인하기 위한 것이다.
파이프라인에서는 별도 스텝으로 돌리고 실패해도 빌드를 세우지 않는다.
"""

import random
import time


def test_flaky_high_failure_rate():
    """약 40% 확률로 실패."""
    assert random.random() > 0.4, "무작위 실패 (의도된 flaky)"


def test_flaky_medium_failure_rate():
    """약 20% 확률로 실패."""
    assert random.random() > 0.2, "무작위 실패 (의도된 flaky)"


def test_flaky_low_failure_rate():
    """약 5% 확률로 실패. 드물게 터지는 유형."""
    assert random.random() > 0.05, "무작위 실패 (의도된 flaky)"


def test_flaky_timing_dependent():
    """짝수 초에만 통과. 시간 의존 테스트의 전형."""
    assert int(time.time()) % 2 == 0, "홀수 초에 실행됨"


def test_slow_but_stable():
    """항상 통과하지만 느리다. 실행시간 리포트용."""
    time.sleep(1.5)
    assert True


def test_moderately_slow():
    time.sleep(0.6)
    assert True
