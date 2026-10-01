"""Core rules for the number guessing game."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import random
from typing import Optional


class GuessValidationError(ValueError):
    """Raised when a guess or game configuration is invalid."""


class GameOverError(RuntimeError):
    """Raised when a guess is submitted after the game has ended."""


class GuessFeedback(Enum):
    """Possible outcomes from submitting a guess."""

    TOO_LOW = auto()
    TOO_HIGH = auto()
    CORRECT = auto()
    REPEATED = auto()


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Constraints used by a game session."""

    lower_bound: int = 1
    upper_bound: int = 100
    max_attempts: int = 7

    def __post_init__(self) -> None:
        if isinstance(self.lower_bound, bool) or not isinstance(self.lower_bound, int):
            raise GuessValidationError("lower_bound must be an integer")
        if isinstance(self.upper_bound, bool) or not isinstance(self.upper_bound, int):
            raise GuessValidationError("upper_bound must be an integer")
        if self.lower_bound >= self.upper_bound:
            raise GuessValidationError("lower_bound must be less than upper_bound")
        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int):
            raise GuessValidationError("max_attempts must be an integer")
        if self.max_attempts < 1:
            raise GuessValidationError("max_attempts must be at least 1")


@dataclass(frozen=True, slots=True)
class GuessResult:
    """The result of a valid guess."""

    feedback: GuessFeedback
    guess: int
    attempts_used: int
    remaining_attempts: int

    @property
    def is_correct(self) -> bool:
        """Return whether this guess found the secret number."""

        return self.feedback is GuessFeedback.CORRECT


class NumberGuessingGame:
    """Manage one number guessing session."""

    def __init__(
        self,
        config: Optional[GameConfig] = None,
        *,
        rng: Optional[random.Random] = None,
        secret_number: Optional[int] = None,
    ) -> None:
        self.config = config or GameConfig()
        self._rng = rng or random.Random()
        self._secret_number = (
            self._rng.randint(self.config.lower_bound, self.config.upper_bound)
            if secret_number is None
            else secret_number
        )
        if not self.config.lower_bound <= self._secret_number <= self.config.upper_bound:
            raise GuessValidationError("secret_number must be within the configured range")

        self._attempts_used = 0
        self._guesses: dict[int, None] = {}
        self._won = False

    @property
    def attempts_used(self) -> int:
        """Return the number of valid, non-repeated guesses submitted."""

        return self._attempts_used

    @property
    def remaining_attempts(self) -> int:
        """Return how many attempts remain in this session."""

        return self.config.max_attempts - self._attempts_used

    @property
    def is_over(self) -> bool:
        """Return whether the session has been won or exhausted."""

        return self._won or self.remaining_attempts == 0

    @property
    def won(self) -> bool:
        """Return whether the player has guessed correctly."""

        return self._won

    @property
    def guesses(self) -> tuple[int, ...]:
        """Return valid guesses in the order they were submitted."""

        return tuple(self._guesses)

    @property
    def secret_number(self) -> int:
        """Return the secret number, e.g. to reveal it once the game ends."""

        return self._secret_number

    def make_guess(self, guess: int) -> GuessResult:
        """Submit a guess and return feedback without exposing the secret."""

        if self.is_over:
            raise GameOverError("this game is already over")
        if isinstance(guess, bool) or not isinstance(guess, int):
            raise GuessValidationError("guess must be an integer")
        if not self.config.lower_bound <= guess <= self.config.upper_bound:
            raise GuessValidationError(
                f"guess must be between {self.config.lower_bound} "
                f"and {self.config.upper_bound}"
            )
        if guess in self._guesses:
            return GuessResult(
                GuessFeedback.REPEATED,
                guess,
                self._attempts_used,
                self.remaining_attempts,
            )

        self._guesses[guess] = None
        self._attempts_used += 1
        if guess == self._secret_number:
            self._won = True
            feedback = GuessFeedback.CORRECT
        elif guess < self._secret_number:
            feedback = GuessFeedback.TOO_LOW
        else:
            feedback = GuessFeedback.TOO_HIGH

        return GuessResult(feedback, guess, self._attempts_used, self.remaining_attempts)
