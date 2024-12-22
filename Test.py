import unittest
from unittest.mock import patch, mock_open
import json
from io import StringIO

# Импортируем функции для тестирования
from Confmg3 import parse_json_to_ukya, main

class TestJSONToUKYA(unittest.TestCase):
    def test_simple_translation(self):
        json_input = \
        {
            "value": 42,
            "name": "example",
            "expression": "^{3 + 4}"
        }

        expected_output = (
            "global value = 42\n"
            "global name = 'example'\n"
            "^{+ 3 4} = 7"
        )

        actual_output = parse_json_to_ukya(json_input)
        self.assertEqual(actual_output, expected_output)



    def test_nested_translation(self):
        json_input = \
        {
            "nested_config": {
                "val" : "^{5 + 6}",
                "// nested_comment": "Another single-line comment"
            }
        }

        expected_output = (
            "$[\n"
            "^{+ 5 6} = 11\n"
            "C Another single-line comment\n"
            "]"
        )

        actual_output = parse_json_to_ukya(json_input)
        self.assertEqual(actual_output, expected_output)

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": 10}')
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_success(self, mock_stdout, mock_file):
        with patch("sys.argv", ["main.py", "input.json"]):
            main()  # Вызов основной функции
        self.assertIn("global key = 10", mock_stdout.getvalue())  # Проверка вывода