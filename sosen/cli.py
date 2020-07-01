import requests
import json
from somef import cli as somef_cli

from .get_zenodo_query_data import get_zenodo_query_data
from .data_to_graph import DataGraph
from .schema.keyword_schema import keyword_schema, keyword_prefixes
from .get_data import get_zenodo_data
import math
import os
from rdflib import Graph
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON

from .sparql_queries import get_keyword_matches, get_keyword


def run_scrape(queries, all, graph_out, zenodo_data, threshold, format, data_dict):
    print("running")
    if not zenodo_data:
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
        with open(zenodo_data, "r") as in_file:
            data_and_urls_flattened = json.load(in_file)


    # save the data and urls flattened object
    with open(graph_out + ".data_and_urls.json", "w") as out_file:
        json.dump(data_and_urls_flattened, out_file)

    # make sure that the github urls are all unique, too
    github_urls = {data["github_url"] for data in data_and_urls_flattened.values()}

    cli_data = {}

    if data_dict is not None and os.path.exists(data_dict):
        with open(data_dict, "r") as json_in:
            cli_data = json.load(json_in)

        print(f"found {data_dict} with {len(cli_data)} entries")

    # get the data from the cli
    index = 0
    for github_url in github_urls:
        if github_url not in cli_data:
            index += 1
            data = somef_cli.cli_get_data(threshold, repo_url=github_url)
            cli_data.update({github_url: data})

            # save every 10 times... saving is pretty quick.
            if index == 10:
                index = 0
                with open(data_dict, "w") as json_out:
                    json.dump(cli_data, json_out)
                print(f"saved cli_data to {data_dict}")
        else:
            print(f"{github_url} found cached in {data_dict}")


    # save at the end, too
    with open(data_dict, "w") as json_out:
        json.dump(cli_data, json_out)

    filtered_data = (data for data in data_and_urls_flattened.values()
                     if data["github_url"] in cli_data and cli_data[data["github_url"]] is not None)

    document_data = [{**cli_data[data["github_url"]], "zenodo_data": data["zenodo_data"]}
                     for data in filtered_data]

    # create the keywords with document frequencies
    total_documents = len(document_data)
    keyword_frequency = {}

    def make_list(maybe_list):
        if isinstance(maybe_list, list) or isinstance(maybe_list, tuple):
            return maybe_list
        else:
            return [maybe_list]


    for document in document_data:
        topics = document["topics"]
        topics = make_list(topics)
        for keyword_obj in topics:
            keyword_second_list = make_list(keyword_obj["excerpt"])
            for keyword in keyword_second_list:
                if keyword in keyword_frequency:
                    keyword_frequency[keyword] += 1
                else:
                    keyword_frequency[keyword] = 1

    keyword_data = ({"keyword": keyword, "documentFrequency": frequency/total_documents}
                    for keyword, frequency in keyword_frequency.items())

    # add data to graph
    graph = DataGraph()
    for data in document_data:
        graph.add_somef_data(data)

    # add keyword data to graph
    for data in keyword_data:
        graph.add_data(data, keyword_schema, keyword_prefixes)

    with open(graph_out, "wb") as out_file:
        out_file.write(graph.g.serialize(format=format))

def run_get_data(queries, output, graph_in):
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


def run_search(keywords, graph_in):
    keywords = [keyword.lower() for keyword in keywords]
    all_keywords = get_all_keywords(keywords)
    sparql = SPARQLWrapper(graph_in)

    keyword_dfs = {}

    # first, get all of the keywords and their frequencies
    for keyword in all_keywords:
        query_string = get_keyword.format(keyword=keyword)
        sparql.setQuery(query_string)
        # print(query_string)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()

        # there's only 1 or 0 results but this is an easier way of writing that
        for result in results['results']['bindings']:
            keyword_id = result['keyword_id']['value']
            keyword_df = result['keyword_df']['value']
            keyword_dfs[keyword_id] = float(keyword_df)

    # now, get the documents that match these keywords
    all_results = {}
    for keyword_id, keyword_df in keyword_dfs.items():
        query_string = get_keyword_matches.format(keyword_id=keyword_id)
        sparql.setQuery(query_string)
        # print(query_string)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()

        # calculate the idf
        keyword_idf = -1 * math.log(keyword_df, math.e)

        print(f"keyword: {keyword_id}, idf: {keyword_idf}")

        for result in results['results']['bindings']:
            obj_id = result['obj']['value']
            keyword_count = result['keyword_count']['value']

            if obj_id in all_results:
                all_results[obj_id]['keyword_idf_sum'] += keyword_idf
            else:
                all_results[obj_id] = {
                    'keyword_idf_sum': keyword_idf,
                    'keyword_count': int(keyword_count)
                }

    # all_results = {}
    # for keyword in all_keywords:
    #     query_string = get_keyword_matches.format(keyword=keyword)
    #     sparql.setQuery(query_string)
    #     print(query_string)
    #     sparql.setReturnFormat(SPARQL_JSON)
    #     results = sparql.query().convert()
    #
    #     for result in results['results']['bindings']:
    #         obj_id = result['obj']['value']
    #         keyword_count = result['keyword_count']['value']
    #
    #         if obj_id in all_results:
    #             all_results[obj_id]['keyword_matches'] += 1
    #         else:
    #             all_results[obj_id] = {
    #                 'keyword_matches': 1,
    #                 'keyword_count': int(keyword_count)
    #             }

    tf_idf_results = [{"obj_id": obj_id, "tf_idf": value['keyword_idf_sum']/value['keyword_count']}
                      for obj_id, value in all_results.items()]

    tf_idf_results.sort(key=lambda obj: obj["tf_idf"], reverse=True)

    for index, result in enumerate(tf_idf_results):
        if index >= 20:
            break
        print(result)


