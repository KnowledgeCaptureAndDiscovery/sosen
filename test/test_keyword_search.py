import unittest
from sosen.cli import get_all_keywords

class Base(unittest.TestCase):
    pass

class TestGetAllKeywords(Base):
    def test_basic(self):
        keywords = ["a", "b", "c"]
        all_keywords = get_all_keywords(keywords)
        expected_keywords = ["a", "a-b", "a-b-c", "b", "b-c", "c"]

        # asserting same size and one is subset of other asserts set equality
        self.assertEqual(len(all_keywords), len(expected_keywords))
        for keyword in all_keywords:
            self.assertIn(keyword, expected_keywords)