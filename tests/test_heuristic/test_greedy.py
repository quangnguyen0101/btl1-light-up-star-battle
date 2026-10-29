"""Test Greedy Best-First trên dữ liệu thật và trên hợp đồng kết quả."""
import unittest
from pathlib import Path

from src.blind_search import ALGORITHMS as BLIND_ALGORITHMS
from src.heuristic import ALGORITHMS
from src.model.result import empty_state, validate_result
from src.model.star_battle import StarBattleProblem
from src.utils import load_problem

ROOT = Path(__file__).resolve().parents[2]
GREEDY = ALGORITHMS["greedy"]
BLIND = BLIND_ALGORITHMS

SMALL = (
    "star_battle/sb-5x5-normal-03.json",
    "star_battle/sb-6x6-shapeless-01.json",
    "light_up/lu-7x7-normal-03.json",
    "light_up/lu-7x7-easy-01.json",
)


class TestGreedy(unittest.TestCase):
    def test_solves_small_puzzles(self):
        for name in SMALL:
            with self.subTest(puzzle=name):
                problem = load_problem(ROOT / "data" / name)
                result = GREEDY(problem)

                self.assertTrue(result["solution"], name)
                self.assertTrue(problem.is_goal(result["state"]), name)
                self.assertGreater(result["expanded"], 0)

    def test_contract(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-5x5-normal-03.json")
        result = GREEDY(problem)

        self.assertEqual(validate_result(problem, result), [])
        self.assertEqual(result["path"][0], empty_state(problem))
        self.assertEqual(
            result["path"][-1], problem.state_from_coords(result["solution"])
        )

    def test_light_up_path_starts_at_empty_board(self):
        problem = load_problem(ROOT / "data" / "light_up/lu-7x7-normal-03.json")
        result = GREEDY(problem)

        self.assertEqual(validate_result(problem, result), [])
        self.assertEqual(result["path"][0], empty_state(problem))
        self.assertTrue(all(problem.is_valid_state(s) for s in result["path"]))

    def test_no_solution(self):
        # 2x2, một sao mỗi hàng/cột: mọi cách đặt đều kề chéo nhau.
        problem = StarBattleProblem.from_dict({
            "name": "impossible",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 2,
            "cols": 2,
            "stars_per_unit": 1,
        })
        result = GREEDY(problem)

        self.assertEqual(result["solution"], [])
        self.assertIsNone(result["state"])
        self.assertEqual(result["path"], [])
        self.assertEqual(validate_result(problem, result), [])

    def test_agrees_with_dfs_on_goal(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-6x6-shapeless-01.json")
        greedy = GREEDY(problem)
        dfs = BLIND["dfs"](problem)

        self.assertTrue(problem.is_goal(greedy["state"]))
        self.assertTrue(problem.is_goal(dfs["state"]))


if __name__ == "__main__":
    unittest.main()
