"""Input model, illumination and rule validation for Light Up / Akari."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


Coord = tuple[int, int]
WALLS = {"#", "0", "1", "2", "3", "4"}

@dataclass(frozen=True)
class LightUpProblem:
    name: str
    rows: int
    cols: int
    grid: tuple[tuple[str, ...], ...]
    known_solution: tuple[Coord, ...] | None = None

    @staticmethod
    def _validate_coord_data(coord, rows: int, cols: int) -> Coord:
        if (
            not isinstance(coord, (list, tuple))
            or len(coord) != 2
            or any(
                not isinstance(x, int) or isinstance(x, bool)
                for x in coord
            )
        ):
            raise ValueError(f"Invalid solution coordinate: {coord!r}")

        r, c = coord
        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError(
                f"Solution coordinate out of bounds: {coord!r}"
            )

        return r, c

    @classmethod
    def from_dict(cls, data: dict) -> "LightUpProblem":
        required = {"name", "type", "rows", "cols", "grid"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")
        if data["type"] != "light_up":
            raise ValueError("type must be 'light_up'")
        rows, cols = data["rows"], data["cols"]
        if not isinstance(rows, int) or isinstance(rows, bool) or not isinstance(cols, int) or isinstance(cols, bool) or rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive integers")
        grid = tuple(tuple(str(cell) for cell in row) for row in data["grid"])
        if len(grid) != rows or any(len(row) != cols for row in grid):
            raise ValueError("grid must have exactly rows x cols entries")
        if any(cell not in {".", "#", "0", "1", "2", "3", "4"} for row in grid for cell in row):
            raise ValueError("grid cells must be '.', '#', or a digit from '0' to '4'")
        known_solution = data.get("known_solution")

        if known_solution is not None:
            known_solution = tuple(
                cls._validate_coord_data(coord, rows, cols)
                for coord in known_solution
            )

        return cls(
            data["name"],
            rows,
            cols,
            grid,
            known_solution,
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "LightUpProblem":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def state_from_coords(self, bulbs: Iterable[Coord]) -> tuple[int, ...]:
        masks = [0] * self.rows
        for coord in bulbs:
            r, c = self._coord(coord)
            if self.grid[r][c] != ".":
                raise ValueError(f"Bulb can only be placed on a white cell: {coord}")
            masks[r] |= 1 << c
        return tuple(masks)

    def coords_from_state(self, state: tuple[int, ...]) -> list[Coord]:
        self._check_state_shape(state)
        return [(r, c) for r, mask in enumerate(state) for c in range(self.cols) if mask & (1 << c)]

    def _coord(self, coord) -> Coord:
        if not isinstance(coord, (list, tuple)) or len(coord) != 2 or any(not isinstance(x, int) or isinstance(x, bool) for x in coord):
            raise ValueError(f"Invalid coordinate: {coord!r}; expected [row, col]")
        r, c = coord
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError(f"Coordinate out of bounds: {coord!r}")
        return r, c

    def _check_state_shape(self, state: tuple[int, ...]) -> None:
        if len(state) != self.rows or any(not isinstance(m, int) or m < 0 or m >= (1 << self.cols) for m in state):
            raise ValueError("State must contain one valid bitmask per row")
        for r, mask in enumerate(state):
            for c in range(self.cols):
                if mask & (1 << c) and self.grid[r][c] != ".":
                    raise ValueError("A bulb cannot occupy a wall cell")

    def illuminated_cells(self, state: tuple[int, ...]) -> frozenset[Coord]:
        self._check_state_shape(state)
        lit: set[Coord] = set()
        for r, c in self.coords_from_state(state):
            lit.add((r, c))
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                rr, cc = r + dr, c + dc
                while 0 <= rr < self.rows and 0 <= cc < self.cols and self.grid[rr][cc] == ".":
                    lit.add((rr, cc))
                    rr += dr
                    cc += dc
        return frozenset(lit)

    def is_valid_state(self, state: tuple[int, ...], *, require_all_lit: bool = False) -> bool:
        try:
            self._check_state_shape(state)
        except (ValueError, TypeError):
            return False
        bulbs = set(self.coords_from_state(state))
        for r, c in bulbs:
            for dr, dc in ((1, 0), (0, 1)):
                rr, cc = r + dr, c + dc
                while 0 <= rr < self.rows and 0 <= cc < self.cols and self.grid[rr][cc] == ".":
                    if (rr, cc) in bulbs:
                        return False
                    rr += dr
                    cc += dc
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell in "01234":
                    adjacent = sum((rr, cc) in bulbs for rr, cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0 <= rr < self.rows and 0 <= cc < self.cols)
                    if adjacent > int(cell):
                        return False
                    if require_all_lit and adjacent != int(cell):
                        return False
        if require_all_lit:
            whites = {(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] == "."}
            if not whites.issubset(self.illuminated_cells(state)):
                return False
        return True

    def is_goal(self, state: tuple[int, ...]) -> bool:
        return self.is_valid_state(state, require_all_lit=True)

    def render(self, state: tuple[int, ...]) -> str:
        lit = self.illuminated_cells(state)
        lines = []
        for r in range(self.rows):
            chars = []
            for c in range(self.cols):
                cell = self.grid[r][c]
                if state[r] & (1 << c): chars.append("B")
                elif cell == ".": chars.append("*" if (r, c) in lit else ".")
                else: chars.append(cell)
            lines.append(" ".join(chars))
        return "\n".join(lines)
