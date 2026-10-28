"""Test A* trên dữ liệu thật và trên hợp đồng kết quả."""
import unittest
from pathlib import Path

from src.heuristic import ALGORITHMS
from src.model.result import empty_state, validate_result
from src.utils import load_problem

ROOT = Path(__file__).resolve().parents[2]
A_STAR = ALGORITHMS["a_star"]

SMALL = (
    "star_battle/sb-5x5-normal-03.json",
    "star_battle/sb-6x6-shapeless-01.json",
    "light_up/lu-7x7-normal-03.json",
    "light_up/lu-7x7-easy-01.json",
)


class TestAStar(unittest.TestCase):
    def test_solves_small_puzzles(self):
        for name in SMALL:
            with self.subTest(puzzle=name):
                problem = load_problem(ROOT / "data" / name)
                result = A_STAR(problem)

                self.assertTrue(result["solution"], name)
                self.assertTrue(problem.is_goal(result["state"]), name)
                self.assertGreater(result["expanded"], 0)

    def test_contract(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-5x5-normal-03.json")
        result = A_STAR(problem)

        self.assertEqual(validate_result(problem, result), [])
        self.assertEqual(result["path"][0], empty_state(problem))
        self.assertEqual(
            result["path"][-1], problem.state_from_coords(result["solution"])
        )

    def test_light_up_path_starts_at_empty_board(self):
        """Gốc của A* Light Up là trạng thái sau lan truyền, không phải bàn trống."""
        problem = load_problem(ROOT / "data" / "light_up/lu-7x7-normal-03.json")
        result = A_STAR(problem)

        self.assertEqual(result["path"][0], empty_state(problem))
        bulbs_in_root = sum(mask.bit_count() for mask in result["path"][1])
        self.assertGreater(bulbs_in_root, 0, "lan truyen phai dat san bong bat buoc")

    def test_large_puzzle(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-10x10-normal-01.json")
        result = A_STAR(problem)

        self.assertTrue(problem.is_goal(result["state"]))
        self.assertGreater(result["expanded"], 1000)

    def test_agrees_with_dfs_on_small_puzzle(self):
        from src.blind_search import ALGORITHMS as BLIND

        problem = load_problem(ROOT / "data" / "star_battle/sb-6x6-shapeless-01.json")
        mine = A_STAR(problem)
        other = BLIND["dfs"](problem)

        self.assertTrue(problem.is_goal(mine["state"]))
        self.assertTrue(problem.is_goal(other["state"]))


if __name__ == "__main__":
    unittest.main()
