import unittest
from unittest.mock import patch, Mock
import requests
from core import explain_letter, parse_result, format_result, LetterEaseError

VALID = '{"summary":"The letter asks for documents.","action_required":["Submit them by 30.10.2026."],"important_details":["Reference: STU-2026/00421."]}'

class CoreTests(unittest.TestCase):
    def test_three_sections(self):
        text = format_result(parse_result(VALID))
        self.assertEqual(len(text.split('\n\n')), 3)
        self.assertIn('30.10.2026', text)
        self.assertIn('STU-2026/00421', text)

    def test_invalid_formats(self):
        for raw in ('not json', '{}', '[]', VALID.replace('"summary"', '"extra"'), VALID.replace('"Submit them by 30.10.2026."', '42')):
            with self.subTest(raw=raw), self.assertRaises(LetterEaseError):
                parse_result(raw)

    @patch('core.requests.post')
    def test_request_and_success(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {'choices': [{'finish_reason': 'stop', 'message': {'content': VALID}}]}
        self.assertEqual(explain_letter('Datum: 14.10.2026', 'test-key', 'test-model')['summary'], 'The letter asks for documents.')
        args = post.call_args.kwargs
        self.assertEqual(args['headers']['Authorization'], 'Bearer test-key')
        self.assertIn('14.10.2026', args['json']['messages'][1]['content'])
        self.assertFalse(args['allow_redirects'])

    @patch('core.requests.post')
    def test_failures_and_truncation(self, post):
        for code in (401, 403, 429, 500):
            post.return_value = Mock(status_code=code)
            with self.assertRaises(LetterEaseError):
                explain_letter('letter', 'key', 'model')
        post.side_effect = requests.Timeout()
        with self.assertRaises(LetterEaseError):
            explain_letter('letter', 'key', 'model')
        post.side_effect = None
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {'choices': [{'finish_reason': 'length', 'message': {'content': VALID}}]}
        with self.assertRaises(LetterEaseError):
            explain_letter('letter', 'key', 'model')

    @patch('core.requests.post')
    def test_validation_before_network(self, post):
        for letter, key in [('', 'key'), ('a' * 30001, 'key'), ('letter', '')]:
            with self.assertRaises(LetterEaseError):
                explain_letter(letter, key, 'model')
        post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
