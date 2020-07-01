import unittest
from sosen.cli import run_scrape
import os

# run the whole process on a file and verify the output is as expected


class BaseEndToEnd(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        pass


class FromCached(BaseEndToEnd):

    def test_end_to_end_from_cached(self):
        self.from_cached_helper(
            "test_data_and_urls.json",
            "test_data_dict.json",
            "test_actual_out.ttl",
            "test_expected_out.ttl"
        )
        self.from_cached_helper(
            "test_long_data_and_urls.json",
            "test_long_data_dict.json",
            "test_long_actual_out.ttl",
            "test_long_expected_out.ttl"
        )

    def from_cached_helper(self, zenodo_file, dict_file, graph_file, out_file):
        abs_path = os.path.abspath(os.path.dirname(__file__))
        print(abs_path)

        queries = None
        all = None
        zenodo_data = os.path.join(abs_path, zenodo_file)
        data_dict = os.path.join(abs_path, dict_file)
        graph_out = os.path.join(abs_path, graph_file)
        expected_out_file = os.path.join(abs_path, out_file)
        threshold = 0.8
        format = "turtle"

        run_scrape(
            queries=queries,
            all=all,
            zenodo_data=zenodo_data,
            data_dict=data_dict,
            graph_out=graph_out,
            threshold=threshold,
            format=format
        )

        with open(graph_out, "r") as actual_in:
            actual_out = actual_in.read()

        with open(expected_out_file, "r") as expected_in:
            expected_out = expected_in.read()

        self.assertEqual(actual_out, expected_out)


