
"""Input model and rule validation for Star Battle."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


Coord = tuple[int, int]


def _coord(value, rows: int, cols: int) -> Coord:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or any(
            not isinstance(x, int) or isinstance(x, bool)
            for x in value
        )
    ):
        raise ValueError(
            f"Invalid coordinate: {value!r}; expected [row, col]"
        )

    r, c = value

    if not (0 <= r < rows and 0 <= c < cols):
        raise ValueError(f"Coordinate out of bounds: {value!r}")

    return r, c


@dataclass(frozen=True)
class StarBattleProblem:
    name: str
    rows: int
    cols: int
    stars_per_unit: int
    regions: tuple[tuple[int | str, ...], ...] | None = None
    blocked_cells: frozenset[Coord] = frozenset()
    variant: str = "normal"
    known_solution: tuple[Coord, ...] | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "StarBattleProblem":
        required = {
            "name", "type", "rows", "cols", "stars_per_unit"
        }
        missing = required - data.keys()

        if missing:
            raise ValueError(
                f"Missing required fields: {sorted(missing)}"
            )

        if data["type"] != "star_battle":
            raise ValueError("type must be 'star_battle'")

        rows = data["rows"]
        cols = data["cols"]
        k = data["stars_per_unit"]

        if not all(
            isinstance(x, int) and not isinstance(x, bool)
            for x in (rows, cols, k)
        ) or rows <= 0 or cols <= 0 or k <= 0:
            raise ValueError(
                "rows, cols and stars_per_unit must be positive integers"
            )

        # Each row and column must contain k stars.
        # Therefore, the total row and column capacities must match.
        if rows != cols:
            raise ValueError(
                "Star Battle requires a square board when each "
                "row and column has the same star count"
            )

        # Infer the variant if it is not explicitly specified.
        default_variant = (
            "normal" if data.get("regions") is not None
            else "shapeless"
        )
        variant = data.get("variant", default_variant)

        if variant not in {"normal", "shapeless"}:
            raise ValueError(
                "variant must be 'normal' or 'shapeless'"
            )

        regions = None

        if variant == "normal":
            if data.get("regions") is None:
                raise ValueError(
                    "Normal Star Battle requires regions"
                )

            raw_regions = data["regions"]

            if (
                not isinstance(raw_regions, list)
                or len(raw_regions) != rows
                or any(
                    not isinstance(row, list) or len(row) != cols
                    for row in raw_regions
                )
            ):
                raise ValueError(
                    "regions must have exactly rows x cols entries"
                )

            for row in raw_regions:
                for value in row:
                    if (
                        not isinstance(value, (int, str))
                        or isinstance(value, bool)
                    ):
                        raise ValueError(
                            "Region IDs must be integers or strings"
                        )

            regions = tuple(
                tuple(row) for row in raw_regions
            )

            region_ids = {
                value for row in regions for value in row
            }

            if len(region_ids) != rows:
                raise ValueError(
                    "Normal Star Battle requires exactly "
                    "one distinct region per row count"
                )

        elif data.get("regions") is not None:
            raise ValueError(
                "Shapeless Star Battle must not define regions"
            )

        blocked = frozenset(
            _coord(cell, rows, cols)
            for cell in data.get("blocked_cells", [])
        )

        known_solution = data.get("known_solution")
        if known_solution is not None:
            known_solution = tuple(
                _coord(cell, rows, cols)
                for cell in known_solution
            )

        return cls(
            name=data["name"],
            rows=rows,
            cols=cols,
            stars_per_unit=k,
            regions=regions,
            blocked_cells=blocked,
            variant=variant,
            known_solution=known_solution,
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "StarBattleProblem":
        data = json.loads(
            Path(path).read_text(encoding="utf-8")
        )
        return cls.from_dict(data)

    def state_from_coords(
        self, stars: Iterable[Coord]
    ) -> tuple[int, ...]:
        masks = [0] * self.rows

        for raw in stars:
            r, c = _coord(raw, self.rows, self.cols)

            if (r, c) in self.blocked_cells:
                raise ValueError(
                    f"Cannot place a star on a blocked cell: {(r, c)}"
                )

            masks[r] |= 1 << c

        return tuple(masks)

    def coords_from_state(
        self, state: tuple[int, ...]
    ) -> list[Coord]:
        self._validate_state_shape(state)

        return [
            (r, c)
            for r, mask in enumerate(state)
            for c in range(self.cols)
            if mask & (1 << c)
        ]

    def _validate_state_shape(
        self, state: tuple[int, ...]
    ) -> None:
        if (
            not isinstance(state, (tuple, list))
            or len(state) != self.rows
            or any(
                not isinstance(mask, int)
                or isinstance(mask, bool)
                or mask < 0
                or mask >= (1 << self.cols)
                for mask in state
            )
        ):
            raise ValueError(
                "State must contain one valid bitmask per row"
            )

    def is_valid_state(
        self,
        state: tuple[int, ...],
        *,
        partial: bool = False,
    ) -> bool:
        try:
            self._validate_state_shape(state)
        except (ValueError, TypeError):
            return False

        # Check the number of stars in each row.
        row_counts = [mask.bit_count() for mask in state]

        if any(
            count > self.stars_per_unit
            or (
                not partial
                and count != self.stars_per_unit
            )
            for count in row_counts
        ):
            return False

        # Check columns and blocked cells.
        col_counts = [0] * self.cols

        for r, mask in enumerate(state):
            for c in range(self.cols):
                if not (mask & (1 << c)):
                    continue

                if (r, c) in self.blocked_cells:
                    return False

                col_counts[c] += 1

        if any(
            count > self.stars_per_unit
            or (
                not partial
                and count != self.stars_per_unit
            )
            for count in col_counts
        ):
            return False

        # Stars cannot touch horizontally, vertically,
        # or diagonally, including across adjacent rows.
        for r, mask in enumerate(state):
            for c in range(self.cols):
                if not (mask & (1 << c)):
                    continue

                # Check the cell immediately to the right.
                if c + 1 < self.cols and mask & (1 << (c + 1)):
                    return False

                # Check the three neighboring cells in the next row.
                if r + 1 < self.rows:
                    for cc in range(
                        max(0, c - 1),
                        min(self.cols, c + 2),
                    ):
                        if state[r + 1] & (1 << cc):
                            return False

        # Only Normal Star Battle has region constraints.
        if self.variant == "normal":
            assert self.regions is not None
            region_counts = {
                rid: 0
                for row in self.regions
                for rid in row
            }

            for r, mask in enumerate(state):
                for c in range(self.cols):
                    if mask & (1 << c):
                        rid = self.regions[r][c]
                        region_counts[rid] += 1

            if any(
                count > self.stars_per_unit
                or (
                    not partial
                    and count != self.stars_per_unit
                )
                for count in region_counts.values()
            ):
                return False

        return True

    def is_goal(self, state: tuple[int, ...]) -> bool:
        return self.is_valid_state(state, partial=False)

    def render(self, state: tuple[int, ...]) -> str:
        self._validate_state_shape(state)

        lines = []

        for r in range(self.rows):
            chars = []

            for c in range(self.cols):
                if state[r] & (1 << c):
                    chars.append("★")
                elif (r, c) in self.blocked_cells:
                    chars.append("×")
                else:
                    chars.append(".")

            lines.append(" ".join(chars))

        return "\n".join(lines)
