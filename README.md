# Tangram calendar solver

The goal of the project is to compute solution(s?) to a calendar puzzle.

![Exemple of such a calendar](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F61rk41yA6eL._AC_SL1500_.jpg)

The exact calendar shape, pieces shape and their colors may change between editions.


## Usage

As of today, you need to edit the `GRID` in `solver.py` to mark reserved cells for the day (put something else than `None`).

Then you can run the solver:

```bash
./solver.py
[['black', 'black', 'black', -2, 'green', 'green'],
 ['blue', 'blue', 'black', 'black', 'green', 'green'],
 ['blue', 'white', 'white', 'white', 'green', 'green', 'yellow'],
 ['blue', 'red', 'red', 'white', 'orange', 'orange', 'yellow'],
 ['blue', -2, 'red', 'white', 'orange', 'yellow', 'yellow'],
 ['purple', 'purple', 'red', 'red', 'orange', 'orange', 'yellow'],
 ['purple', 'purple', 'purple']]
```

## Contributing

Some tests have already been integrated. You can run them with:

```bash
python -m unittest solver.py
```

Also as of today, the solver doesn't require any external dependency and no warning are generated neither by `flakes8`, `pylint` nor `ruff`.


## TODO

Exemple of future developements:
- Have an output more human readable
- Add Arguments to:
  - Enter a date (today by default)
  - Don't stop at the first solution
  - Auto-run unittest
- Let the algorithm compute all orientations for a piece shape
- Run tests in CI
