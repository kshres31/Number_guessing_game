"""Command line interface for the number guessing game."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .game import (
    GameConfig,
    GuessFeedback,
    GuessResult,
    GuessValidationError,
    NumberGuessingGame,
)

DEFAULT_LOWER_BOUND = 1
DEFAULT_UPPER_BOUND = 100
DEFAULT_MAX_ATTEMPTS = 7


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the game."""

    parser = argparse.ArgumentParser(
        prog="guess-the-number",
        description="Guess the secret number before you run out of attempts.",
    )
    parser.add_argument(
        "--min",
        type=int,
        default=DEFAULT_LOWER_BOUND,
        dest="lower_bound",
        help=f"lowest possible secret number (default: {DEFAULT_LOWER_BOUND})",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=DEFAULT_UPPER_BOUND,
        dest="upper_bound",
        help=f"highest possible secret number (default: {DEFAULT_UPPER_BOUND})",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=DEFAULT_MAX_ATTEMPTS,
        dest="max_attempts",
        help=f"maximum number of attempts (default: {DEFAULT_MAX_ATTEMPTS})",
    )
    parser.add_argument(
        "--secret",
        type=int,
        default=None,
        help="force a specific secret number (useful for demos and tests)",
    )
    return parser


def _parse_guess(line: str) -> Optional[int]:
    """Convert raw input to an integer, or None (and print a message) if invalid."""

    text = line.strip()
    try:
        return int(text)
    except ValueError:
        print(f'"{text}" is not a number. Try again.')
        return None


def _announce(result: GuessResult) -> None:
    """Print the outcome of a guess."""

    if result.feedback is GuessFeedback.TOO_LOW:
        print("Too low!")
    elif result.feedback is GuessFeedback.TOO_HIGH:
        print("Too high!")
    elif result.feedback is GuessFeedback.REPEATED:
        print(f"You already guessed {result.guess}. Try a different number.")


def play(game: NumberGuessingGame) -> int:
    """Run an interactive session until the player wins or runs out of attempts."""

    print(
        f"I'm thinking of a number between {game.config.lower_bound} "
        f"and {game.config.upper_bound}."
    )
    print(f"You have {game.config.max_attempts} attempts to find it. Good luck!")

    while not game.is_over:
        try:
            line = input(f"Guess ({game.remaining_attempts} left): ")
        except EOFError:
            print("Goodbye!")
            return 1

        guess = _parse_guess(line)
        if guess is None:
            continue

        try:
            result = game.make_guess(guess)
        except GuessValidationError as exc:
            print(exc)
            continue

        _announce(result)
        if result.is_correct:
            attempts = result.attempts_used
            noun = "attempt" if attempts == 1 else "attempts"
            print(f"Correct! You found {result.guess} in {attempts} {noun}.")
            return 0

    print(f"Out of attempts! The number was {game.secret_number}.")
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse arguments and play one game. Returns the process exit code."""

    args = build_parser().parse_args(argv)
    try:
        config = GameConfig(args.lower_bound, args.upper_bound, args.max_attempts)
        game = NumberGuessingGame(config, secret_number=args.secret)
    except GuessValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return play(game)


if __name__ == "__main__":
    raise SystemExit(main())
