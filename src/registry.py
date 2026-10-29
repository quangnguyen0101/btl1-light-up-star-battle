"""Tên thuật toán -> (họ thuật toán, hàm chạy).

Thêm thuật toán mới chỉ cần thêm một dòng ở đây; ``scripts/run.py`` và
``scripts/compare.py`` tự biết thư mục output tương ứng.
"""
from src.blind_search.registry import ALGORITHMS as BLIND_SEARCH
from src.heuristic.registry import ALGORITHMS as HEURISTIC
from src.local_search.registry import ALGORITHMS as LOCAL_SEARCH

ALGORITHMS = {
    "dfs": ("blind_search", BLIND_SEARCH["dfs"]),
    "a_star": ("heuristic", HEURISTIC["a_star"]),
    "greedy": ("heuristic", HEURISTIC["greedy"]),
    "simulated_annealing": ("local_search", LOCAL_SEARCH["simulated_annealing"]),
}

__all__ = ["ALGORITHMS"]
