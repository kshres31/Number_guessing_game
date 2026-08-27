# Number Guessing Game

A classic command line number guessing game written in Python. The computer
picks a secret number and you try to find it in as few attempts as possible,
getting "too low" / "too high" hints after every guess.

## Features

- Configurable number range and attempt limit via command line flags
- Handles invalid input (non-numbers, out-of-range guesses, repeated guesses)
  without ending the game
- Repeats of an already-used guess do not consume an attempt
- Clean separation between the game engine and the CLI, so the rules are easy
  to reuse or test
- Zero runtime dependencies (standard library only)

## Requirements

- Python 3.10 or newer

## Installation

Clone the repository, then run the game directly from the checkout:

```bash
python -m number_guessing_game
```

Or install it as a package to get the `guess-the-number` command:

```bash
python -m pip install -e .
guess-the-number
```

## Usage

```
$ python -m number_guessing_game
I'm thinking of a number between 1 and 100.
You have 7 attempts to find it. Good luck!
Guess (7 left): 50
Too high!
Guess (6 left): 25
Too low!
Guess (5 left): 37
Correct! You found 37 in 3 attempts.
```

### Options

| Flag          | Description                                        | Default |
| ------------- | -------------------------------------------------- | ------- |
| `--min N`     | Lowest possible secret number                      | 1       |
| `--max N`     | Highest possible secret number                     | 100     |
| `--attempts N`| Maximum number of attempts                         | 7       |
| `--secret N`  | Force a specific secret number (demos and tests)   | random  |

Example: a hard round on a 1–1000 range with only 5 attempts:

```bash
python -m number_guessing_game --min 1 --max 1000 --attempts 5
```

The process exits with code `0` when the player wins and `1` when the player
loses or quits. Invalid command line configuration (for example `--min 100
--max 1`) exits with code `2`.

## Using the engine as a library

```python
from number_guessing_game import GameConfig, GuessFeedback, NumberGuessingGame

game = NumberGuessingGame(GameConfig(1, 100, 7))  # random secret

result = game.make_guess(50)
if result.feedback is GuessFeedback.TOO_LOW:
    print("50 is too low")
```

The `secret_number` argument is available for deterministic tests and demos.
`GuessResult` exposes `feedback`, `attempts_used`, `remaining_attempts`, and
`is_correct`.

## Running the tests

Tests use the standard library `unittest` framework, so no extra dependencies
are required:

```bash
python -m unittest discover -s tests -v
```

Alternatively, install the dev extras and use pytest:

```bash
python -m pip install -e ".[dev]"
pytest
```

## Project structure

```
number_guessing_game/
├── __init__.py   # public API
├── __main__.py   # enables `python -m number_guessing_game`
├── game.py       # game rules, configuration, validation
└── cli.py        # command line interface
tests/
├── test_game.py  # unit tests for the game engine
└── test_cli.py   # tests for the command line interface
pyproject.toml    # packaging and entry point
```

## Future ideas

- Difficulty presets (easy / medium / hard)
- A high-score table stored on disk
- Statistics across rounds (average attempts, win rate)
