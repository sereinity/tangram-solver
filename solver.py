#!/bin/env python
"""
Tangram infinte-calendar solver.
"""

import copy
import datetime
import sys
import unittest
from argparse import ArgumentParser
from collections import deque
from contextlib import contextmanager
from io import StringIO
from random import shuffle
from unittest.mock import patch


def put_shape(grid, shape, shape_id) -> None:
    """
    Put the shape in the first free grid position.
    """
    free_pos = find_next_cell_with(grid)
    offset = find_next_cell_with(shape, 1)[1]
    next_pos = free_pos.copy()
    next_pos[1] -= offset
    if next_pos[1] < 0:
        raise CantPutError("Out of bound")
    for line in shape:
        for col in line:
            try:
                if col == 1 and grid[next_pos[0]][next_pos[1]] is not None:
                    raise CantPutError("Not free cell", next_pos)
                if col == 1:
                    grid[next_pos[0]][next_pos[1]] = shape_id
            except IndexError as exc:
                raise CantPutError("Out of bound") from exc
            next_pos[1] += 1
        next_pos[1] = free_pos[1] - offset
        next_pos[0] += 1


def find_next_cell_with(grid, search=None):
    """
    Returns the coordinates of the first cell holding `search`.
    """
    for line_no, line in enumerate(grid):
        try:
            col_no = line.index(search)
            return [line_no, col_no]
        except ValueError:
            pass
    return None


def main() -> None:
    """
    Perform the recursive search and then print the result.
    """
    args = parse_args()
    date = args.date if args.date else datetime.date.today()
    grid = copy.deepcopy(GRID)
    pieces = copy.deepcopy(PIECES)
    mark_date(grid, date)
    if args.all:
        item_id = 0
        for item_id, solution in enumerate(recursive_search(grid, pieces)):
            print_grid(solution)
        print(f"Found {item_id + 1} solutions")
    else:
        shuffle(pieces)
        print_grid(next(recursive_search(grid, pieces)))


def parse_args(args=None):
    """
    Create argument parser and return the Namespace object.
    """
    aparser = ArgumentParser(description=__doc__)
    aparser.add_argument(
        "--date",
        "-d",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
        help="The date to print (example 2025-04-16, today by default)",
    )
    aparser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="activate to search for all solutions",
    )
    return aparser.parse_args(args)


def recursive_search(grid, available_pieces):
    """
    Recursively search for a solution.
    """
    for piece in available_pieces:
        for shape in piece.orientations:
            w_grid = copy.deepcopy(grid)
            try:
                put_shape(w_grid, shape, piece.repr)
            except CantPutError:
                continue
            w_avail_pieces = available_pieces.copy()
            w_avail_pieces.remove(piece)
            if find_next_cell_with(w_grid) is None:
                yield w_grid
            yield from recursive_search(w_grid, w_avail_pieces)


def mark_date(grid, date):
    """
    Return the grid with given month and day reserved.
    """
    (line, col) = divmod(date.month - 1, 6)
    grid[line][col] = "□"
    (line, col) = divmod(date.day - 1, 7)
    grid[line + 2][col] = "□"
    return grid


def print_grid(grid) -> None:
    """
    Print the grid on the screen on a human readable way.
    """
    print("".join(["-"] * 13))
    deque(map(lambda x: print(" ".join(x)), grid))


class CantPutError(Exception):
    """
    Can't put the piece here.
    """


class Piece:
    """
    Piece representation, useful to manipulate it.
    """

    def __init__(self, shape, prepr) -> None:
        self.shape = shape
        self.repr = prepr
        self.orientations = set()
        self._generate_orientations()

    def _generate_orientations(self) -> None:
        """
        Compute all possible orientation (flip included) simplify it
        and store it into the object.
        """
        orientations = [self.shape]
        for _ in range(3):
            orientations.append(self.rotate(orientations[-1]))
        orientations.append(self.flip())
        for _ in range(3):
            orientations.append(self.rotate(orientations[-1]))
        self.orientations = set(orientations)

    def flip(self):
        """
        Get the current piece in a reversed state.
        """
        return tuple(reversed(self.shape))

    @staticmethod
    def rotate(shape):
        """
        Returns a rotated (90°) version of the given shape.
        """
        return tuple(zip(*shape[::-1]))


class ShapeTest(unittest.TestCase):
    """
    Test that all pieces have a correct shape.
    """

    def test_find_free_cell(self) -> None:
        """
        Test we can find free cell in grids.
        """
        grid = [[None, None, 1, 1], [None, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [0, 0])
        grid = [[1, None, 1, 1], [None, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [0, 1])
        grid = [[1, 1, 1, 1], [1, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [1, 1])

    def test_cant_find_free_cell(self) -> None:
        """
        Test we can't find free cell in full grids.
        """
        grid = [[1, 2, 1, 1], [1, 2, 1, 1]]
        self.assertEqual(find_next_cell_with(grid), None)

    def test_can_put(self) -> None:
        """
        Test that the piece can fit.
        """
        grid = [[None, None, 1, 1], [None, None, None, None]]
        shape = [[1, 1, 0, 0], [0, 1, 1, 1]]
        put_shape(grid, shape, "x")
        self.assertListEqual(
            [["x", "x", 1, 1], [None, "x", "x", "x"]],
            grid,
        )

    def test_can_put_with_blank(self) -> None:
        """
        Test that the piece with an empty first cell in shape can fit.
        """
        grid = [[1, None, None, None], [None, None, None, None]]
        shape = [[0, 1, 1, 1], [1, 1, 0, 0]]
        put_shape(grid, shape, "x")
        self.assertListEqual(
            [[1, "x", "x", "x"], ["x", "x", None, None]],
            grid,
        )

    def test_cannot_put_with_negative_offset(self) -> None:
        """
        Test that the piece with an empty first cell can't be put in first
        column.
        """
        grid = [[None, None, None, None], [None, None, None, None]]
        shape = [[0, 1, 1, 1], [1, 1, 0, 0]]
        with self.assertRaises(CantPutError) as exp:
            put_shape(grid, shape, "x")
        self.assertEqual(exp.exception.args, ("Out of bound",))

    def test_cant_put(self) -> None:
        """
        Test that the piece can't fit and is rejected.
        """
        grid = [[None, None, 1, 1], [None, None, None, 1]]
        shape = [[1, 1, 0, 0], [0, 1, 1, 1]]
        with self.assertRaises(CantPutError) as cp:
            put_shape(grid, shape, "x")
        self.assertEqual(cp.exception.args, ("Not free cell", [1, 3]))

    def test_cant_put_outside(self) -> None:
        """
        Test that the piece can't be placed outside of the grid.
        """
        grid = [[None, None, None], [None, None, None]]
        shape = [[1, 1, 0, 0], [0, 1, 1, 1]]
        with self.assertRaises(CantPutError) as cp:
            put_shape(grid, shape, "x")
        self.assertEqual(cp.exception.args, ("Out of bound",))

    def test_flip(self) -> None:
        """
        The flip produces a wanted result.
        """
        piece = Piece(
            (
                (0, 1, 1, 0),
                (1, 1, 0, 0),
                (0, 1, 1, 1),
            ),
            "x",
        )
        self.assertEqual(
            piece.flip(),
            ((0, 1, 1, 1), (1, 1, 0, 0), (0, 1, 1, 0)),
        )

    def test_four_rotate(self) -> None:
        """
        Rotating four times a piece should give the initial state.
        """
        piece = Piece(
            (
                (0, 1, 1, 0),
                (1, 1, 0, 0),
                (0, 1, 1, 1),
            ),
            "x",
        )
        first_rotate = piece.rotate(piece.shape)
        self.assertEqual(
            first_rotate,
            ((0, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)),
        )
        last_rotate = piece.rotate(piece.rotate(piece.rotate(first_rotate)))
        self.assertEqual(last_rotate, piece.shape)


class MainTest(unittest.TestCase):
    """
    Run tests on the main process.
    """

    def test_mark_date(self) -> None:
        """
        Test that we can mark april the 18th.
        """
        grid = mark_date(copy.deepcopy(GRID), datetime.date(2025, 4, 18))
        self.assertEqual(
            grid,
            [
                [None, None, None, "□", None, None],
                [None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, "□", None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None],
            ],
        )

    def test_parse_args(self) -> None:
        """
        Test that we correctly parse date in argument parser.
        """
        args = parse_args(["--date", "2025-04-17"])
        self.assertEqual(args.all, False)
        self.assertEqual(args.date, datetime.datetime(2025, 4, 17))

    def test_resolve_one(self) -> None:
        """
        Resolve a specific grid.
        """
        date = datetime.date(2025, 4, 18)
        grid = copy.deepcopy(GRID)
        mark_date(grid, date)
        solution = next(recursive_search(grid, PIECES))
        self.assertEqual(
            solution,
            [
                ["X", "X", "X", "□", "/", "/"],
                ["-", "-", "X", "X", "▲", "/"],
                ["-", "●", "●", "●", "▲", "/", "/"],
                ["-", "●", "H", "●", "▲", "▲", "▲"],
                ["-", "|", "H", "□", "■", "■", "■"],
                ["|", "|", "H", "H", "■", "■", "■"],
                ["|", "|", "H"],
            ],
        )

    @patch("argparse._sys.argv", ["solver.py", "--date", "2025-04-17"])
    def test_full_run_single_grid(self) -> None:
        """
        Test that we can get a grid solution.
        """
        with captured_output() as (out, err):
            main()
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(len(out.getvalue().splitlines()), 8)

    @patch(
        "argparse._sys.argv", ["solver.py", "--all", "--date", "2025-04-17"]
    )
    def test_full_run_all_grids(self) -> None:
        """
        Test that we can get a grid solution.
        """
        with captured_output() as (out, err):
            main()
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(out.getvalue().splitlines()[-1], "Found 62 solutions")


@contextmanager
def captured_output():
    """
    Patch tool that help capturing stdout/stderr during tests.
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


GRID = (
    [[None] * 6 for _ in range(2)]
    + [[None] * 7 for _ in range(2, 6)]
    + [[None] * 3]
)

PIECES = [
    Piece(((1, 1, 0, 0), (0, 1, 1, 1)), "X"),
    Piece(((1, 0, 0, 0), (1, 1, 1, 1)), "-"),
    Piece(((1, 1), (1, 1), (1, 1)), "■"),
    Piece(((1, 1, 1), (1, 0, 1)), "●"),
    Piece(((1, 0), (1, 1), (1, 1)), "|"),
    Piece(((1, 0, 0), (1, 1, 1), (0, 0, 1)), "/"),
    Piece(((1, 0, 0), (1, 0, 0), (1, 1, 1)), "▲"),
    Piece(((0, 1, 0, 0), (1, 1, 1, 1)), "H"),
]


if __name__ == "__main__":
    main()
