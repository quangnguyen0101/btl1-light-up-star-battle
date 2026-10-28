"""Ngắt một lời gọi tìm kiếm khi quá hạn (chỉ trên POSIX)."""
from __future__ import annotations

import signal
from contextlib import contextmanager


class Timeout(Exception):
    """Lời gọi tìm kiếm bị ngắt vì quá thời gian cho phép."""


@contextmanager
def timeout(seconds: float | None):
    """Ngắt khối lệnh bên trong sau ``seconds`` giây.

    Không có ``SIGALRM`` (Windows) hoặc ``seconds`` là ``None`` thì chạy không
    giới hạn -- bài toán vẫn cho kết quả, chỉ là không có hạn chót.
    """
    usable = (
        seconds is not None
        and seconds > 0
        and hasattr(signal, "setitimer")
        and hasattr(signal, "SIGALRM")
    )
    if not usable:
        yield
        return

    def _raise(signum, frame):
        raise Timeout(f"qua {seconds}s")

    previous = signal.signal(signal.SIGALRM, _raise)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
