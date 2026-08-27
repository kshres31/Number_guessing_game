"""Tests for the command line interface."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from number_guessing_game.cli import main


class CliTest(unittest.TestCase):
    def _run(self, inputs, argv=None):
        """Run main() feeding `inputs` as answers, returning (exit code, output)."""

        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch("builtins.input", side_effect=inputs),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            code = main(argv)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_winning_game(self):
        code, out = self._run(
            ["50", "75", "63"],
            argv=["--secret", "63"],
        )
        self.assertEqual(code, 0)
        self.assertIn("Too low!", out)
        self.assertIn("Too high!", out)
        self.assertIn("Correct! You found 63 in 3 attempts.", out)

    def test_win_on_first_attempt(self):
        code, out = self._run(["42"], argv=["--secret", "42"])
        self.assertEqual(code, 0)
        self.assertIn("in 1 attempt.", out)

    def test_loss_when_attempts_run_out(self):
        code, out = self._run(
            ["10", "20", "30", "40"],
            argv=["--secret", "99", "--attempts", "4"],
        )
        self.assertEqual(code, 1)
        self.assertIn("Out of attempts!", out)
        self.assertIn("The number was 99", out)

    def test_non_numeric_input_retries(self):
        code, out = self._run(["abc", "50"], argv=["--secret", "50"])
        self.assertEqual(code, 0)
        self.assertIn('"abc" is not a number.', out)

    def test_out_of_range_guess_retries(self):
        code, out = self._run(["0", "101", "50"], argv=["--secret", "50"])
        self.assertEqual(code, 0)
        self.assertIn("guess must be between 1 and 100", out)

    def test_repeated_guess_is_reported(self):
        code, out = self._run(["10", "10", "50"], argv=["--secret", "50"])
        self.assertEqual(code, 0)
        self.assertIn("You already guessed 10.", out)

    def test_invalid_config_exits_with_error(self):
        code, out = self._run([], argv=["--min", "100", "--max", "1"])
        self.assertEqual(code, 2)
        self.assertIn("error:", out)

    def test_secret_outside_range_exits_with_error(self):
        code, out = self._run([], argv=["--secret", "0"])
        self.assertEqual(code, 2)
        self.assertIn("error:", out)

    def test_eof_quits_cleanly(self):
        stdout = io.StringIO()
        with mock.patch("builtins.input", side_effect=EOFError), redirect_stdout(stdout):
            code = main(["--secret", "50"])
        self.assertEqual(code, 1)
        self.assertIn("Goodbye!", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
