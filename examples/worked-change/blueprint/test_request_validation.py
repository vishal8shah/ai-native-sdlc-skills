import unittest

from request_validation import request_is_valid


class RequestIsValidTests(unittest.TestCase):
    def test_missing_justification(self):
        self.assertIs(request_is_valid(), False)
        self.assertIs(request_is_valid(None), False)

    def test_empty_and_whitespace_only_justification(self):
        for value in ("", " ", "\t\n\r", " \t \n ", "\u2003\u00a0"):
            with self.subTest(value=repr(value)):
                self.assertIs(request_is_valid(value), False)

    def test_nonblank_justification(self):
        for value in ("Reason", "  Reason\n", "0", "\u2003理由\u00a0"):
            with self.subTest(value=value):
                self.assertIs(request_is_valid(value), True)

    def test_non_string_input(self):
        for value in (0, 1, 1.5, False, True, [], {}, b"Reason", object()):
            with self.subTest(value=repr(value)):
                self.assertIs(request_is_valid(value), False)


if __name__ == "__main__":
    unittest.main()
