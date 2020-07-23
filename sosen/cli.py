import json
from somef import cli as somef_cli

from .get_zenodo_query_data import get_zenodo_query_data
from .data_to_graph import DataGraph
from .keywords import KeywordCounter, ExistingKeywordCounter
from .schema.global_schema import global_prefixes, global_schema
from .schema.keyword_schema import keyword_schema, keyword_prefixes, keyword_in_software_schema,\
    description_keyword_relationship_schema, title_keyword_relationship_schema, keyword_relationship_schema
from .get_data import get_zenodo_data
import math
import os
from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON

from .sparql_queries import get_software_from_kw, compare_softwares
from .config import get_config

from rdflib import RDF, Namespace
from rdflib.util import guess_format
from .schema.schema_prefixes import sd
SD = Namespace(sd)

from tabulate import tabulate
from textwrap import wrap as text_wrap

def run_scrape(queries, all, graph_out, keyword_out, zenodo_in, zenodo_cache, threshold, data_dict):
    print("running")
    if not zenodo_in:
        if all:
            queries = {""}
        else:
            with open(queries, "r") as in_handle:
                # get all of the queries
                queries = {stripped_line for stripped_line in
                           (line.rstrip("\n") for line in in_handle)
                           # if len(stripped_line) > 0
                           }

        print(queries)
        # get the data from zenodo for each
        data_and_urls = (get_zenodo_data(query) for query in queries)

        # flatten it all into one object and use a dict to guarantee uniqueness
        data_and_urls_flattened = {}
        total_len = 0
        for dict_obj in data_and_urls:
            total_len += len(dict_obj)
            data_and_urls_flattened.update(dict_obj)
            print(f"total len: {len(data_and_urls_flattened)}, total gathered: {total_len}, repeats: {total_len - len(data_and_urls_flattened)}")

    else:
        with open(zenodo_in, "r") as in_file:
            data_and_urls_flattened = json.load(in_file)


    # save the data and urls flattened object
    if zenodo_cache is not None:
        with open(zenodo_cache, "w") as out_file:
            json.dump(data_and_urls_flattened, out_file)

    # do not proceed unless we have an output graph or output data_dict
    if graph_out is None and data_dict is None:
        return

    zenodo_data = {}
    # change data_and_urls so that it is indexed by github url
    for zenodo_id, data in data_and_urls_flattened.items():
        if data is not None:
            github_url = data["github_url"]
            if github_url not in zenodo_data:
                zenodo_data[github_url] = []

            zenodo_data[github_url].append(
                {"data": data["data"], "version": data["version"]}
            )

    cli_data = {}

    if data_dict is not None and os.path.exists(data_dict):
        with open(data_dict, "r") as json_in:
            cli_data = json.load(json_in)

        print(f"found {data_dict} with {len(cli_data)} entries")

    # get the data from the cli
    index = 0
    for github_url, object_data in zenodo_data.items():
        if github_url not in cli_data:
            index += 1
            data = somef_cli.cli_get_data(threshold, repo_url=github_url)
            cli_data[github_url] = data

            # save every 10 times... saving is pretty quick.
            if index == 10:
                index = 0
                if data_dict:
                    with open(data_dict, "w") as json_out:
                        json.dump(cli_data, json_out)
                    print(f"saved cli_data to {data_dict}")
        else:
            print(f"{github_url} found cached in {data_dict}")

    # save at the end, too
    if data_dict:
        with open(data_dict, "w") as json_out:
            json.dump(cli_data, json_out)

    document_data = [{**cli_data[github_url], "zenodo_data": data}
                     for github_url, data in zenodo_data.items()
                     if data is not None and cli_data[github_url] is not None]

    # get total number of software entities
    total_documents = len(document_data)

    # add data to graph
    graph = DataGraph()
    for data in document_data:
        graph.add_somef_data(data)

    graph_out_format = guess_format(graph_out)
    print(f"saving graph to {graph_out} as {graph_out_format} format")
    with open(graph_out, "wb") as out_file:
        out_file.write(graph.g.serialize(format=graph_out_format))

    # end early if there is no keyword file
    if keyword_out is None:
        return

    # search through graph to add the description keyword data
    kw_graph = DataGraph()

    software_ids = []
    full_descriptions = []
    software_names = []
    keywords_dict = {}
    for software_id, _, _ in graph.g.triples((None, RDF.type, SD.Software)):
        full_descriptions.append("\n".join([str(description) for _, _, description in
                                      graph.g.triples((software_id, SD.description, None))]))
        software_names.append("\n".join([str(name) for _, _, name in
                                   graph.g.triples((software_id, SD.name, None))]))
        keywords_dict[software_id] = [
            str(keyword) for _, _, keyword in graph.g.triples((software_id, SD.keywords, None))
        ]
        software_ids.append(software_id)

    # setup the counters
    description_counter = KeywordCounter(software_ids, full_descriptions)
    description_keyword_data = description_counter.get_keyword_data()
    description_keyword_relationship_data = description_counter.get_keyword_relationship_data()

    title_counter = KeywordCounter(software_ids, software_names)
    title_keyword_data = title_counter.get_keyword_data()
    title_keyword_relationship_data = title_counter.get_keyword_relationship_data()

    keyword_counter = ExistingKeywordCounter(keywords_dict)
    keyword_data = keyword_counter.get_keyword_data()
    keyword_relationship_data = keyword_counter.get_keyword_relationship_data()

    # merge the keywords
    def merge_with_prop_name(source, dest, prop_name):
        for key, value in source.items():
            if key not in dest:
                dest[key] = {
                    "descriptionInCount": 0,
                    "titleInCount": 0,
                    "keywordInCount": 0
                }

            dest[key][prop_name] = value

        return dest

    all_keyword_data = {}
    all_keyword_data = merge_with_prop_name(
        description_keyword_data,
        all_keyword_data,
        "descriptionInCount"
    )
    all_keyword_data = merge_with_prop_name(
        title_keyword_data,
        all_keyword_data,
        "titleInCount"
    )
    all_keyword_data = merge_with_prop_name(
        keyword_data,
        all_keyword_data,
        "keywordInCount"
    )
    # flatten and add to the graph
    all_keyword_data_list = [
        {"keyword": keyword, **data} for keyword, data in all_keyword_data.items()
    ]
    kw_graph.add_data(all_keyword_data_list, keyword_schema, keyword_prefixes)

    # add the keywords to the software
    def merge_relationships(source, dest, count_name, keywords_name):
        for key, value in source.items():
            if key not in dest:
                dest[key] = {}

            dest[key][count_name] = value["count"]
            dest[key][keywords_name] = value["keywords"]

        return dest

    all_relationships = merge_relationships(
        description_keyword_relationship_data,
        {},
        "descriptionKeywordCount",
        "descriptionKeywords"
    )
    all_relationships = merge_relationships(
        title_keyword_relationship_data,
        all_relationships,
        "titleKeywordCount",
        "titleKeywords"
    )
    all_relationships = merge_relationships(
        keyword_relationship_data,
        all_relationships,
        "keywordCount",
        "keywords"
    )

    all_relationships_list = [
        {"id": key, **value} for key, value in all_relationships.items()
    ]

    kw_graph.add_data(all_relationships_list, keyword_in_software_schema, keyword_prefixes)

    # but we'll have to make 3 calls for the relationships (one for each type)
    kw_graph.add_data(all_relationships_list, description_keyword_relationship_schema, keyword_prefixes)
    kw_graph.add_data(all_relationships_list, title_keyword_relationship_schema, keyword_prefixes)
    kw_graph.add_data(all_relationships_list, keyword_relationship_schema, keyword_prefixes)



    global_data = {
        "totalSoftwareCount": total_documents
    }

    kw_graph.add_data(global_data, global_schema, global_prefixes)

    kw_graph_format = guess_format(keyword_out)
    print(f"writing keyword graph to {keyword_out} as {kw_graph_format} format")
    with open(keyword_out, "wb") as out_file:
        out_file.write(kw_graph.g.serialize(format=kw_graph_format))


def run_get_data(queries, output):
    graph_in = get_config()["endpoint"]
    sparql = SPARQLWrapper(graph_in)

    with open(queries, "r") as query_file:
        print("loading queries")
        queries_set = {stripped_line for stripped_line in
                   (line.rstrip("\n") for line in query_file)
                   if len(stripped_line) > 0
                   }
        print("querying API")
        output_data = {query: get_zenodo_query_data(query, sparql) for query in queries_set}

    print("saving data")
    with open(output, "w") as out_file:
        json.dump(output_data, out_file)


def get_all_keywords(keywords):
    if len(keywords) == 0:
        return []

    keywords_using_first = ["-".join(keywords[0:index+1]) for index, _ in enumerate(keywords)]
    other_keywords = get_all_keywords(keywords[1:])

    return [*keywords_using_first, *other_keywords]


def run_search(keywords, method="description"):
    if isinstance(keywords, str):
        keywords = keywords.split(" ")

    graph_in = get_config()["endpoint"]
    sparql = SPARQLWrapper(graph_in)

    keywords = [keyword.lower() for keyword in keywords]
    if method == "keyword":
        keywords = get_all_keywords(keywords)

    results = get_software_from_kw(keywords, method, sparql)

    table_data = [
        [
            index + 1,
            result['software']['value'],
            result['matches']['value'],
            result['sum_tf_idf']['value']
        ]
        for index, result in enumerate(results)
    ]

    print("\nMATCHES:")

    print(tabulate(
        table_data,
        headers=["", "result iri", "matches", "tf-idf sum"],
        # tablefmt="github"
    ))


def run_describe(iris):
    graph_in = get_config()["endpoint"]
    sparql = SPARQLWrapper(graph_in)

    text_width = 50

    data = compare_softwares(iris, sparql)


    # table = [
    #     ["" if line_index != 0 else property if value_index == 0 else '" "', value_line]
    #     for property, values in data
    #     for value_index, value in enumerate(values)
    #     for line_index, value_line in enumerate(text_wrap(value, width=text_width))
    # ]
    table = []
    for row in data:
        key = row[0]
        row_values = row[1:]
        print(f"{key}: {row_values}")
        count_row_values = max([len(value) for value in row_values])
        print(f"count row values: {count_row_values}")
        for index in range(count_row_values):
            print(f"index: {index}")
            print(f"first row val: {row_values[0]}")
            values = [(row_value[index] if index < len(row_value) else "") for row_value in row_values]
            wrapped_values = [text_wrap(value, width=text_width) for value in values]
            print(wrapped_values)
            max_line_length = max([len(lines) for lines in wrapped_values])
            print(f"max line len: {max_line_length}")
            out_rows = [
                [
                    "" if line_index != 0 else key if index == 0 else '" "',
                    *[
                        wrapped_value[line_index] if line_index < len(wrapped_value) else ""
                        for wrapped_value in wrapped_values
                    ]
                ]
                for line_index in range(max_line_length)
            ]

            table += out_rows


    print(table)

    print(tabulate(
        table,
        headers=["property"] + [f"software {i+1}" for i in range(len(iris))],
        tablefmt="github"
    ))









