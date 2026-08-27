"""Unit tests for the core game engine."""

import random
import unittest

from number_guessing_game import (
    GameConfig,
    GameOverError,
    GuessFeedback,
    GuessValidationError,
    NumberGuessingGame,
)


class GameConfigTest(unittest.TestCase):
    def test_defaults(self):
        config = GameConfig()
        self.assertEqual(
            (config.lower_bound, config.upper_bound, config.max_attempts),
            (1, 100, 7),
        )

    def test_rejects_invalid_bounds(self):
        for kwargs in (
            {"lower_bound": "1"},
            {"lower_bound": True},
            {"upper_bound": 3.5},
            {"lower_bound": 50, "upper_bound": 50},
            {"lower_bound": 90, "upper_bound": 10},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(GuessValidationError):
                    GameConfig(**kwargs)

    def test_rejects_invalid_attempts(self):
        for kwargs in (
            {"max_attempts": 0},
            {"max_attempts": -3},
            {"max_attempts": "7"},
            {"max_attempts": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(GuessValidationError):
                    GameConfig(**kwargs)


class NumberGuessingGameTest(unittest.TestCase):
    def test_guess_below_secret(self):
        game = NumberGuessingGame(secret_number=42)
        result = game.make_guess(10)
        self.assertIs(result.feedback, GuessFeedback.TOO_LOW)
        self.assertFalse(result.is_correct)
        self.assertEqual(result.attempts_used, 1)
        self.assertEqual(result.remaining_attempts, 6)

    def test_guess_above_secret(self):
        game = NumberGuessingGame(secret_number=42)
        result = game.make_guess(99)
        self.assertIs(result.feedback, GuessFeedback.TOO_HIGH)

    def test_correct_guess_wins(self):
        game = NumberGuessingGame(secret_number=42)
        result = game.make_guess(42)
        self.assertIs(result.feedback, GuessFeedback.CORRECT)
        self.assertTrue(result.is_correct)
        self.assertTrue(game.won)
        self.assertTrue(game.is_over)
        self.assertEqual(game.attempts_used, 1)

    def test_repeated_guess_does_not_consume_an_attempt(self):
        game = NumberGuessingGame(secret_number=42)
        game.make_guess(10)
        result = game.make_guess(10)
        self.assertIs(result.feedback, GuessFeedback.REPEATED)
        self.assertEqual(game.attempts_used, 1)
        self.assertEqual(game.remaining_attempts, 6)

    def test_out_of_range_guess_rejected(self):
        game = NumberGuessingGame(secret_number=42)
        with self.assertRaises(GuessValidationError):
            game.make_guess(0)
        with self.assertRaises(GuessValidationError):
            game.make_guess(101)

    def test_non_integer_guess_rejected(self):
        game = NumberGuessingGame(secret_number=42)
        for bad in ("42", 42.0, True):
            with self.subTest(bad=bad):
                with self.assertRaises(GuessValidationError):
                    game.make_guess(bad)

    def test_game_ends_after_max_attempts(self):
        game = NumberGuessingGame(GameConfig(max_attempts=3), secret_number=42)
        self.assertFalse(game.is_over)
        game.make_guess(1)
        game.make_guess(2)
        self.assertFalse(game.is_over)
        result = game.make_guess(3)
        self.assertFalse(result.is_correct)
        self.assertTrue(game.is_over)
        self.assertEqual(game.remaining_attempts, 0)
        self.assertFalse(game.won)
        with self.assertRaises(GameOverError):
            game.make_guess(4)

    def test_guess_after_win_raises(self):
        game = NumberGuessingGame(secret_number=7)
        game.make_guess(7)
        with self.assertRaises(GameOverError):
            game.make_guess(8)

    def test_secret_number_outside_range_rejected(self):
        with self.assertRaises(GuessValidationError):
            NumberGuessingGame(secret_number=0)
        with self.assertRaises(GuessValidationError):
            NumberGuessingGame(GameConfig(1, 10, 5), secret_number=11)

    def test_random_secret_stays_in_range(self):
        for _ in range(200):
            game = NumberGuessingGame()
            self.assertGreaterEqual(game.secret_number, game.config.lower_bound)
            self.assertLessEqual(game.secret_number, game.config.upper_bound)

    def test_seeded_rng_is_reproducible(self):
        first = NumberGuessingGame(rng=random.Random(42)).secret_number
        second = NumberGuessingGame(rng=random.Random(42)).secret_number
        self.assertEqual(first, second)

    def test_guesses_recorded_in_order(self):
        game = NumberGuessingGame(secret_number=42)
        game.make_guess(10)
        game.make_guess(60)
        self.assertEqual(game.guesses, (10, 60))


if __name__ == "__main__":
    unittest.main()
