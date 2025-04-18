# Tangram calendar solver

The goal of the project is to compute solution(s?) to a calendar puzzle.

![Exemple of such a calendar](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F61rk41yA6eL._AC_SL1500_.jpg)

The exact calendar shape, pieces shape and their colors may change between editions.


## Usage

Then you can run the solver:

```bash
./solver.py
Tangram infinte-calendar solver

options:
  -h, --help       show this help message and exit
  --date, -d DATE  The date to print (example 2025-04-16, today by default)
  --all, -a        activate to search for all solutions

./solver.py
-------------
X X X □ ■ ■
− − X X ■ ■
− ▲ ▲ ▲ ■ ■ H
− / / ▲ ● ● H
− □ / ▲ ● H H
| | / / ● ● H
| | |
```

## Contributing

Some tests have already been integrated. You can run them with:

```bash
coverage run
coverage report
Name        Stmts   Miss Branch BrPart  Cover
---------------------------------------------
solver.py     180      1     28      1    99%
---------------------------------------------
TOTAL         180      1     28      1    99%
```

Also as of today, the solver doesn't require any external dependency and no warning are generated neither by `ruff`.

```bash
ruff check
```


## TODO

Exemple of future developements:
- Run tests in CI
