import unittest
from sosen.data_to_graph import DataGraph


class Base(unittest.TestCase):
    maxDiff = None
    def setUp(self):
        pass
    # def test_basic(self):
    #     test_software = {
    #         "fullName": "test/test",
    #         "description": "test",
    #         "owner": {
    #             "login": "test"
    #         }
    #     }
    #
    #     schema_table = {
    #         "@class": "sd:Software",
    #         "@id": {
    #             "@format": "obj:Software/{name}",
    #             "name": "fullName"
    #         },
    #         "sd:name": {
    #             "@value": "fullName",
    #             "@type": "xsd:string"
    #         },
    #         "sd:description": {
    #             "@value": "description",
    #             "@type": "xsd:string"
    #         },
    #         "sd:hasAuthor": {
    #             "@class": "schema:Person",
    #             "@id": {
    #                 "@format": "obj:Person/{name}",
    #                 "name": ["owner", "login"]
    #             },
    #             "sd:additionalName": {
    #                 "@value": ["owner", "login"],
    #                 "@type": "schema:Text"
    #             }
    #         }
    #     }
    #
    #     data_graph = DataGraph()
    #     data_graph.somef_to_graph(test_software, schema_table)
    #
    #     for triple in data_graph.g:
    #         print(triple)

class FlattenDict(Base):
    def test_combine_dict(self):

        dict_in = {
            "x": 1,
            "y": [1, 2],
            "z": [[1, 2], ["a", "b"]]
        }

        dict_out = [
            [
                {"x": 1, "y": 1, "z": 1},
                {"x": 1, "y": 1, "z": 2}
            ],
            [
                {"x": 1, "y": 2, "z": "a"},
                {"x": 1, "y": 2, "z": "b"}
            ]
        ]
        dict_actual_out = DataGraph.combine_dict(dict_in)
        for i, _ in enumerate(dict_out):
            for j, _ in enumerate(dict_out[i]):
                self.assertDictEqual(dict_out[i][j], dict_actual_out[i][j])

    def test_combine_dict_method(self):
        dict_in = {
            "x": 1,
            "y": [1, 2]
        }

        string_out = [
            "1/1", "1/2"
        ]

        actual_out = DataGraph.combine_dict(dict_in, method=lambda x: "{x}/{y}".format(**x))

        for i, _ in enumerate(string_out):
            self.assertEqual(string_out[i], actual_out[i])

    def test_combine_dict_pretty(self):

        dict_in = {
            "fullName": "test_a",
            "language": ["Python", "C++"]
        }

        dict_out = [
            {"fullName": "test_a", "language": "Python"},
            {"fullName": "test_a", "language": "C++"}
        ]

        dict_actual_out = DataGraph.combine_dict(dict_in)
        for i, _ in enumerate(dict_out):
            self.assertDictEqual(dict_out[i], dict_actual_out[i])

    def test_combine_dict_method_pretty(self):
        dict_in = {
            "fullName": "test_a",
            "versions": ["v1", "v2"],
            "languages": [["R", "C"], ["Python", "C", "C++"]]
        }
        first_expected_out = [[
            {"fullName": "test_a", "versions": "v1", "languages": "R"},
            {"fullName": "test_a", "versions": "v1", "languages": "C"},
        ], [
            {"fullName": "test_a", "versions": "v2", "languages": "Python"},
            {"fullName": "test_a", "versions": "v2", "languages": "C"},
            {"fullName": "test_a", "versions": "v2", "languages": "C++"},
        ]]
        out = DataGraph.combine_dict(dict_in)
        self.assertEqual(out, first_expected_out)
        out = DataGraph.combine_dict(
            dict_in, method=lambda x:
            "{fullName}/{versions} uses {languages}".format(**x))
        formatted_expected_out = [[
            "test_a/v1 uses R",
            "test_a/v1 uses C",
        ], [
            "test_a/v2 uses Python",
            "test_a/v2 uses C",
            "test_a/v2 uses C++"
        ]]
        self.assertEqual(out, formatted_expected_out)

class ResolvePath(Base):
    def test_resolve_path_array(self):
        test_obj = {
            "x": [
                {
                    "y": [
                        {
                            "z": 1
                        },
                        {
                            "z": 2
                        }
                    ]
                },
                {
                    "y": [
                        {
                            "z": 3
                        },
                        {
                            "z": 4
                        }
                    ]
                }
            ]
        }

        path = ["x", "y", "z"]

        out = DataGraph.resolve_path(test_obj, path)

        self.assertEqual(out, [[1, 2], [3, 4]])

    def test_resolve_path_array_pretty(self):
        test_obj = {
            "fullName": "test_a",
            "versions": [
                {
                    "tag": "v1",
                    "languages": ["R", "C"]
                },
                {
                    "tag": "v2",
                    "languages": ["Python", "C", "C++"]
                }
            ]
        }
        version_languages_path = ["versions", "languages"]
        expected_out = [["R", "C"], ["Python", "C", "C++"]]

        out = DataGraph.resolve_path(test_obj, version_languages_path)
        self.assertEqual(out, expected_out)

# class EndToEnd(Base):
#     def test_pretty(self):
#         example_somef_output = {
#             "fullName": [{
#                 "excerpt": "test_person/test_repo",
#                 "confidence": 1
#             }],
#             "description": [{
#                 "excerpt": "A test repository",
#                 "confidence": 1
#             }, {
#                 "excerpt": "This project uses A to do B",
#                 "confidence": 0.9
#             }],
#             "releases": [{
#                 "excerpt": {
#                     "tag_name": "v1",
#                 },
#                 "confidence": 1
#             }, {
#                 "excerpt": {
#                     "tag_name": "v2"
#                 },
#                 "confidence": 1
#             }]
#         }
#
#         g = DataGraph()
#         g.add_somef_data(example_somef_output)
#
#         print(g.g.serialize(format="turtle").decode("utf-8"))


if __name__ == '__main__':
    unittest.main()
