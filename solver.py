#!/bin/env python
"""
Tangram infinte-calendar solver
"""

import copy
import datetime
import unittest
from argparse import ArgumentParser

GRID = (
    [[None] * 6 for _ in range(0, 2)] +
    [[None] * 7 for _ in range(2, 6)] +
    [[None] * 3]
)

PIECES = {
    "X": {
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
    "−": {
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
    "■": {
        "shapes": [
            ((1, 1), (1, 1), (1, 1)),
            ((1, 1, 1), (1, 1, 1)),
        ],
    },
    "●": {
        "shapes": [
            ((1, 1, 1), (1, 0, 1)),
            ((1, 1), (0, 1), (1, 1)),
            ((1, 0, 1), (1, 1, 1)),
            ((1, 1), (1, 0), (1, 1)),
        ],
    },
    "|": {
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
    "/": {
        "shapes": [
            ((1, 0, 0), (1, 1, 1), (0, 0, 1)),
            ((0, 1, 1), (0, 1, 0), (1, 1, 0)),
            ((0, 0, 1), (1, 1, 1), (1, 0, 0)),
            ((1, 1, 0), (0, 1, 0), (0, 1, 1)),
        ],
    },
    "▲": {
        "shapes": [
            ((1, 0, 0), (1, 0, 0), (1, 1, 1)),
            ((1, 1, 1), (1, 0, 0), (1, 0, 0)),
            ((1, 1, 1), (0, 0, 1), (0, 0, 1)),
            ((0, 0, 1), (0, 0, 1), (1, 1, 1)),
        ],
    },
    "H": {
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
        context = {
            'results_count': 0,
            'should_stop': not args.all,
        }
        recursive_search(grid, PIECES, context)
        if not context['should_stop']:
            print("Found %d solutions" % (context['results_count']))


def recursive_search(grid, available_pieces, context):
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
                print_grid(w_grid)
                context['results_count'] += 1
                if context['should_stop']:
                    return w_grid
            rec_result = recursive_search(w_grid, w_avail_pieces, context)
            if rec_result is not None:
                return rec_result
    return None


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
    [print(' '.join(line)) for line in grid]


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
