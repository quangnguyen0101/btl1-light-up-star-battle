
import json
import unittest
from pathlib import Path

from src.model.star_battle import StarBattleProblem


ROOT = Path(__file__).resolve().parents[2]
PUZZLE_PATH = ROOT / "data" / "star_battle" / "sb-5x5-normal-03.json"


class TestStarBattle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problem = StarBattleProblem.from_json(PUZZLE_PATH)

        data = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        cls.solution_coords = [
            tuple(coord) for coord in data["known_solution"]
        ]
        cls.solution = cls.problem.state_from_coords(cls.solution_coords)

    def test_loads_input(self):
        self.assertEqual(self.problem.name, "sb-5x5-normal-03")
        self.assertEqual((self.problem.rows, self.problem.cols), (5, 5))
        self.assertEqual(self.problem.stars_per_unit, 1)
        self.assertEqual(self.problem.variant, "normal")
        self.assertIsNotNone(self.problem.regions)

    def test_known_solution_is_goal(self):
        self.assertTrue(self.problem.is_goal(self.solution))

    def test_empty_state_is_valid_partial_but_not_goal(self):
        empty_state = (0,) * self.problem.rows

        self.assertTrue(
            self.problem.is_valid_state(empty_state, partial=True)
        )
        self.assertFalse(self.problem.is_goal(empty_state))

    def test_diagonal_touch_invalid(self):
        state = self.problem.state_from_coords([(0, 0), (1, 1)])

        self.assertFalse(
            self.problem.is_valid_state(state, partial=True)
        )

    def test_same_row_stars_invalid(self):
        state = self.problem.state_from_coords([(0, 0), (0, 2)])

        self.assertFalse(
            self.problem.is_valid_state(state, partial=True)
        )

    def test_same_column_stars_invalid(self):
        state = self.problem.state_from_coords([(0, 0), (2, 0)])

        self.assertFalse(
            self.problem.is_valid_state(state, partial=True)
        )

    def test_wrong_region_counts_invalid(self):
        # Hai sao trong cùng một vùng vi phạm luật Star Battle.
        state = self.problem.state_from_coords([(0, 0), (0, 1)])

        self.assertFalse(
            self.problem.is_valid_state(state, partial=True)
        )

    def test_bitmask_roundtrip(self):
        coords = self.problem.coords_from_state(self.solution)

        self.assertEqual(set(coords), set(self.solution_coords))
        self.assertEqual(len(coords), len(self.solution_coords))

    def test_blocked_cell_cannot_contain_star(self):
        data = {
            "name": "blocked_test",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 3,
            "cols": 3,
            "stars_per_unit": 1,
            "blocked_cells": [[1, 1]],
        }
        problem = StarBattleProblem.from_dict(data)

        with self.assertRaises(ValueError):
            problem.state_from_coords([(1, 1)])

    def test_shapeless_does_not_require_regions(self):
        data = {
            "name": "shapeless_test",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 3,
            "cols": 3,
            "stars_per_unit": 1,
        }
        problem = StarBattleProblem.from_dict(data)

        self.assertIsNone(problem.regions)
        self.assertEqual(problem.variant, "shapeless")

    def test_invalid_state_shape(self):
        self.assertFalse(self.problem.is_valid_state((0, 0)))

    def test_render_state(self):
        rendered = self.problem.render(self.solution)

        self.assertIn("★", rendered)
        self.assertEqual(len(rendered.splitlines()), self.problem.rows)


if __name__ == "__main__":
    unittest.main()
