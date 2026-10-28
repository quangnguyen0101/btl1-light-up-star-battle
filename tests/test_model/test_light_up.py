import unittest
from pathlib import Path

from src.model.light_up import LightUpProblem


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "data" / "light_up" / "lu-7x7-normal-03.json"


class TestLightUp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load puzzle once for all tests."""
        cls.problem = LightUpProblem.from_json(INPUT_FILE)

    def test_loads_input(self):
        """JSON is parsed with the expected dimensions."""
        self.assertEqual(self.problem.name, "lu-7x7-normal-03")
        self.assertEqual(self.problem.rows, 7)
        self.assertEqual(self.problem.cols, 7)
        self.assertEqual(len(self.problem.grid), 7)
        self.assertTrue(all(len(row) == 7 for row in self.problem.grid))

    def test_loads_known_solution(self):
        """Known solution is loaded from JSON."""
        self.assertIsNotNone(self.problem.known_solution)
        self.assertEqual(len(self.problem.known_solution), 8)

    def test_known_solution_is_goal(self):
        """The sample solution satisfies all Light Up rules."""
        state = self.problem.state_from_coords(
            self.problem.known_solution
        )
        self.assertTrue(self.problem.is_goal(state))

    def test_empty_state_is_not_goal(self):
        """An empty board is not a solved puzzle."""
        state = (0,) * self.problem.rows
        self.assertFalse(self.problem.is_goal(state))

    def test_state_round_trip(self):
        """Converting coordinates to state and back preserves bulbs."""
        bulbs = self.problem.known_solution
        state = self.problem.state_from_coords(bulbs)
        recovered = self.problem.coords_from_state(state)

        self.assertEqual(set(recovered), set(bulbs))

    def test_known_solution_has_no_conflicts(self):
        """The sample solution is a valid state."""
        state = self.problem.state_from_coords(
            self.problem.known_solution
        )
        self.assertTrue(self.problem.is_valid_state(state))

    def test_diagonal_bulbs_do_not_conflict(self):
        state = self.problem.state_from_coords([(1, 2), (0, 3)])
        self.assertTrue(self.problem.is_valid_state(state))

    def test_bulbs_in_same_row_conflict(self):
        """Two visible bulbs in the same row are invalid."""
        state = self.problem.state_from_coords([(0, 0), (0, 1)])
        self.assertFalse(self.problem.is_valid_state(state))

    def test_bulbs_in_same_column_conflict(self):
        """Two visible bulbs in the same column are invalid."""
        state = self.problem.state_from_coords([(0, 0), (1, 0)])
        self.assertFalse(self.problem.is_valid_state(state))

    def test_wall_blocks_light(self):
        problem = LightUpProblem.from_dict({
            "name": "wall_blocks_light",
            "type": "light_up",
            "rows": 1,
            "cols": 3,
            "grid": [[".", "#", "."]],
        })

        state = problem.state_from_coords([(0, 0), (0, 2)])
        self.assertTrue(problem.is_valid_state(state))

    def test_reject_bulb_on_wall(self):
        """A bulb cannot be placed on a wall."""
        problem = LightUpProblem.from_dict({
            "name": "wall_test",
            "type": "light_up",
            "rows": 1,
            "cols": 1,
            "grid": [["#"]],
        })

        with self.assertRaises(ValueError):
            problem.state_from_coords([(0, 0)])

    def test_reject_out_of_bounds_coordinate(self):
        """Coordinates outside the board are rejected."""
        with self.assertRaises(ValueError):
            self.problem.state_from_coords([(7, 0)])

    def test_reject_invalid_state_shape(self):
        """State must have one bitmask per row."""
        self.assertFalse(self.problem.is_valid_state((0, 0)))

    def test_reject_bulb_on_numbered_cell(self):
        """A bulb cannot be placed on a numbered cell."""
        with self.assertRaises(ValueError):
            self.problem.state_from_coords([(1, 1)])


if __name__ == "__main__":
    unittest.main()