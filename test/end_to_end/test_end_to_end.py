import unittest
from sosen.cli import run_scrape
import os

# run the whole process on a file and verify the output is as expected


class BaseEndToEnd(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        pass


class FromCached(BaseEndToEnd):

    def testEndToEndFromCached(self):
        abs_path = os.path.abspath(os.path.dirname(__file__))
        print(abs_path)

        queries = None
        all = None
        zenodo_data = os.path.join(abs_path, "test_data_and_urls.json")
        data_dict = os.path.join(abs_path, "test_data_dict.json")
        graph_out = os.path.join(abs_path, "test_actual_out.ttl")
        expected_out_file = os.path.join(abs_path, "test_expected_out.ttl")
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


