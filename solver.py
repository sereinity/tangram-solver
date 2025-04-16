#!/bin/env python
"""
Tangram infinte-calendar solver
"""

import copy
import unittest
from pprint import pprint

GRID = [
    [None, None, None,   -2, None, None],
    [None, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None,   -2, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None, None, None],
]

PIECES = {
    "black": {
        "shapes": [
            ((1, 1, 0, 0), (0, 1, 1, 1)),
            ((0, 1), (1, 1), (1, 0), (1, 0)),
            ((1, 1, 1, 0), (0, 0, 1, 1)),
            ((0, 1), (0, 1), (1, 1), (1, 0)),
            # after the flip
            ((0, 0, 1, 1), (1, 1, 1, 0)),
            ((1, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 1, 1, 1), (1, 1, 0, 0)),
            ((1, 0), (1, 1), (0, 1), (0, 1)),
        ],
    },
    "blue": {
        "shapes": [
            ((1, 0, 0, 0), (1, 1, 1, 1)),
            ((1, 1), (1, 0), (1, 0), (1, 0)),
            ((1, 1, 1, 1), (0, 0, 0, 1)),
            ((0, 1), (0, 1), (0, 1), (1, 1)),
            # after the flip
            ((1, 1, 1, 1), (1, 0, 0, 0)),
            ((1, 1), (0, 1), (0, 1), (0, 1)),
            ((0, 0, 0, 1), (1, 1, 1, 1)),
            ((1, 0), (1, 0), (1, 0), (1, 1)),
        ],
    },
    "green": {
        "shapes": [
            ((1, 1), (1, 1), (1, 1)),
            ((1, 1, 1), (1, 1, 1)),
        ],
    },
    "orange": {
        "shapes": [
            ((1, 1, 1), (1, 0, 1)),
            ((1, 1), (0, 1), (1, 1)),
            ((1, 0, 1), (1, 1, 1)),
            ((1, 1), (1, 0), (1, 1)),
        ],
    },
    "purple": {
        "shapes": [
            ((1, 0), (1, 1), (1, 1)),
            ((1, 1, 1), (1, 1, 0)),
            ((1, 1), (1, 1), (0, 1)),
            ((0, 1, 1), (1, 1, 1)),
            # after the flip
            ((1, 1, 1), (0, 1, 1)),
            ((0, 1), (1, 1), (1, 1)),
            ((1, 1, 0), (1, 1, 1)),
            ((1, 1), (1, 1), (1, 0)),
        ],
    },
    "red": {
        "shapes": [
            ((1, 0, 0), (1, 1, 1), (0, 0, 1)),
            ((0, 1, 1), (0, 1, 0), (1, 1, 0)),
            ((0, 0, 1), (1, 1, 1), (1, 0, 0)),
            ((1, 1, 0), (0, 1, 0), (0, 1, 1)),
        ],
    },
    "white": {
        "shapes": [
            ((1, 0, 0), (1, 0, 0), (1, 1, 1)),
            ((1, 1, 1), (1, 0, 0), (1, 0, 0)),
            ((1, 1, 1), (0, 0, 1), (0, 0, 1)),
            ((0, 0, 1), (0, 0, 1), (1, 1, 1)),
        ],
    },
    "yellow": {
        "shapes": [
            ((0, 1, 0, 0), (1, 1, 1, 1)),
            ((1, 0), (1, 1), (1, 0), (1, 0)),
            ((1, 1, 1, 1), (0, 0, 1, 0)),
            ((0, 1), (0, 1), (1, 1), (0, 1)),
            # after the flip
            ((1, 1, 1, 1), (0, 1, 0, 0)),
            ((0, 1), (1, 1), (0, 1), (0, 1)),
            ((0, 0, 1, 0), (1, 1, 1, 1)),
            ((1, 0), (1, 0), (1, 1), (1, 0)),
        ],
    },
}


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
    print_grid(recursive_search(GRID, PIECES))


def recursive_search(grid, available_pieces):
    """
    recursively search for a solution
    """
    for p_id, piece in available_pieces.items():
        for shape in piece['shapes']:
            w_grid = copy.deepcopy(grid)
            try:
                put_shape(w_grid, shape, p_id)
            except CantPut:
                continue
            w_avail_pieces = available_pieces.copy()
            del w_avail_pieces[p_id]
            if find_next_cell_with(w_grid) is None:
                return w_grid
            if (ret := recursive_search(w_grid, w_avail_pieces)) is not None:
                return ret
    return None


def print_grid(grid):
    """
    Print the grid on the screen on a human readable way
    """
    pprint(grid)


class CantPut(Exception):
    """
    Can't put the piece here
    """


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

    def test_all_piece_have_constent_size(self):
        """
        Test that all pieces doen't change their size
        """
        self.assertEqual(
            all(map(self._test_constent_size, PIECES.values())),
            True)

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

    def _test_constent_size(self, piece):
        """
        Test that the size of a piece doesn't change
        """
        return (len(set(map(self._get_aera_size, piece["shapes"]))) <= 1) and (
            len(set(map(self._get_aera_shape_size, piece["shapes"]))) <= 1
        )

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


if __name__ == "__main__":
    main()
