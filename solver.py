#!/bin/env python
"""
Tangram infinte-calendar solver
"""

import copy
import datetime
import unittest
from argparse import ArgumentParser
from collections import deque


def put_shape(grid, shape, shape_id):
    """
    Put the shape in the first free grid position
    """
    free_pos = find_next_cell_with(grid)
    offset = find_next_cell_with(shape, 1)[1]
    next_pos = free_pos.copy()
    next_pos[1] -= offset
    if next_pos[1] < 0:
        raise CantPut("Out of bound")
    for line in shape:
        for col in line:
            try:
                if col == 1 and grid[next_pos[0]][next_pos[1]] is not None:
                    raise CantPut("Not free cell", next_pos)
                if col == 1:
                    grid[next_pos[0]][next_pos[1]] = shape_id
            except IndexError as exc:
                raise CantPut("Out of bound") from exc
            next_pos[1] += 1
        next_pos[1] = free_pos[1] - offset
        next_pos[0] += 1


def find_next_cell_with(grid, search=None):
    """
    Returns the coordinates of the first cell holding `search`
    """
    for line_no, line in enumerate(grid):
        try:
            col_no = line.index(search)
            return [line_no, col_no]
        except ValueError:
            pass
    return None


def main():
    """
    perform the recursive search and then print the result
    """
    aparser = ArgumentParser(description=__doc__)
    aparser.add_argument(
        '--unittest', '-u',
        action='store_true',
        help='run unittest instead of solving puzzle'
    )
    aparser.add_argument(
        '--date', '-d',
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        help='The date to print (example 2025-04-16, today by default)'
    )
    aparser.add_argument(
        '--all', '-a',
        action='store_true',
        help='activate to search for all solutions',
    )
    args = aparser.parse_args()
    if args.unittest:
        unittest.main(argv=['unittest'])
    else:
        date = args.date if args.date else datetime.date.today()
        grid = copy.deepcopy(GRID)
        mark_date(grid, date)
        if args.all:
            item_id = 0
            for item_id, solution in enumerate(recursive_search(grid, PIECES)):
                print_grid(solution)
            print(f"Found {item_id+1} solutions")
        else:
            print_grid(next(recursive_search(grid, PIECES)))


def recursive_search(grid, available_pieces):
    """
    recursively search for a solution
    """
    for piece in available_pieces:
        for shape in piece.orientations:
            w_grid = copy.deepcopy(grid)
            try:
                put_shape(w_grid, shape, piece.repr)
            except CantPut:
                continue
            w_avail_pieces = available_pieces.copy()
            w_avail_pieces.remove(piece)
            if find_next_cell_with(w_grid) is None:
                yield w_grid
                continue
            yield from recursive_search(w_grid, w_avail_pieces)


def mark_date(grid, date):
    """
    Return the grid with given month and day reserved
    """
    (line, col) = divmod(date.month-1, 6)
    grid[line][col] = '□'
    (line, col) = divmod(date.day-1, 7)
    grid[line+2][col] = '□'
    return grid


def print_grid(grid):
    """
    Print the grid on the screen on a human readable way
    """
    print(''.join(['-']*13))
    deque(map(lambda x: print(' '.join(x)), grid))


class CantPut(Exception):
    """
    Can't put the piece here
    """


class Piece:
    """
    Piece representation, useful to manipulate it
    """

    def __init__(self, shape, prepr):
        self.shape = shape
        self.repr = prepr
        self.orientations = set()
        self._generate_orientations()

    def _generate_orientations(self):
        """
        Compute all possible orientation (flip included) simplify it
        and store it into the object
        """
        orientations = [self.shape]
        for _ in range(0, 3):
            orientations.append(self.rotate(orientations[-1]))
        orientations.append(self.flip())
        for _ in range(0, 3):
            orientations.append(self.rotate(orientations[-1]))
        self.orientations = set(orientations)

    def flip(self):
        """
        Get the current piece in a reversed state
        """
        return tuple(reversed(self.shape))

    @staticmethod
    def rotate(shape):
        """
        returns a rotated (90°) version of the given shape
        """
        return tuple(zip(*shape[::-1]))


class ShapeTest(unittest.TestCase):
    """
    Test that all pieces have a correct shape
    """

    def test_find_free_cell(self):
        """
        Test we can find free cell in grids
        """
        grid = [[None, None, 1, 1], [None, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [0, 0])
        grid = [[1, None, 1, 1], [None, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [0, 1])
        grid = [[1, 1, 1, 1], [1, None, None, None]]
        self.assertListEqual(find_next_cell_with(grid), [1, 1])

    def test_cant_find_free_cell(self):
        """
        Test we can't find free cell in full grids
        """
        grid = [[1, 2, 1, 1], [1, 2, 1, 1]]
        self.assertEqual(find_next_cell_with(grid), None)

    def test_can_put(self):
        """
        Test that the piece can fit
        """
        grid = [[None, None, 1, 1], [None, None, None, None]]
        shape = [[1, 1, 0, 0], [0, 1, 1, 1]]
        put_shape(grid, shape, "x")
        self.assertListEqual(
            [["x", "x", 1, 1], [None, "x", "x", "x"]],
            grid,
        )

    def test_can_put_strange(self):
        """
        Test that the piece with an empty first cell in shape can fit
        """
        grid = [[1, None, None, None], [None, None, None, None]]
        shape = [[0, 1, 1, 1], [1, 1, 0, 0]]
        put_shape(grid, shape, "x")
        self.assertListEqual(
            [[1, "x", "x", "x"], ["x", "x", None, None]],
            grid,
        )

    def test_cant_put(self):
        """
        Test that the piece can't fit and is rejected
        """
        grid = [[None, None, 1, 1], [None, None, None, 1]]
        shape = [[1, 1, 0, 0], [0, 1, 1, 1]]
        with self.assertRaises(CantPut) as cp:
            put_shape(grid, shape, "x")
        self.assertEqual(cp.exception.args, ("Not free cell", [1, 3]))

    def test_flip(self):
        """
        the flip produces a wanted result
        """
        piece = Piece(((0, 1, 1, 0), (1, 1, 0, 0), (0, 1, 1, 1),), 'x')
        self.assertEqual(
            piece.flip(),
            ((0, 1, 1, 1), (1, 1, 0, 0), (0, 1, 1, 0)),
        )

    def test_four_rotate(self):
        """
        rotating four times a piece should give the initial state
        """
        piece = Piece(((0, 1, 1, 0), (1, 1, 0, 0), (0, 1, 1, 1),), 'x')
        first_rotate = piece.rotate(piece.shape)
        self.assertEqual(
            first_rotate,
            ((0, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)),
        )
        last_rotate = piece.rotate(piece.rotate(piece.rotate(first_rotate)))
        self.assertEqual(last_rotate, piece.shape)

    @staticmethod
    def _get_aera_size(piece_shape):
        """
        get the area size of a piece
        """
        return sum(map(sum, piece_shape))

    @staticmethod
    def _get_aera_shape_size(piece_shape):
        """
        get the area size of a shape
        """
        return sum(map(len, piece_shape))


GRID = (
    [[None] * 6 for _ in range(0, 2)] +
    [[None] * 7 for _ in range(2, 6)] +
    [[None] * 3]
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
