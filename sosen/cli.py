import requests
import json
from somef import cli as somef_cli

from .get_zenodo_query_data import get_zenodo_query_data
from .data_to_graph import DataGraph
from .keywords import KeywordCounter, ExistingKeywordCounter
from .schema.global_schema import global_prefixes, global_schema
from .schema.keyword_schema import keyword_schema, keyword_prefixes, keyword_in_software_schema,\
    description_keyword_relationship_schema, title_keyword_relationship_schema, keyword_relationship_schema
from .schema.software_schema import somef_software_schema
from .get_data import get_zenodo_data
import math
import os
from rdflib import Graph
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON

from .sparql_queries import get_keyword_matches, get_keyword, describe_iri
from .sparql_queries import get_description_keyword, get_document_from_description_kw, get_global_doc_count
from .config import get_config

from rdflib import RDF, Namespace
from .schema.schema_prefixes import sd
SD = Namespace(sd)

from sklearn.feature_extraction.text import CountVectorizer

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

    # get total number of software entities
    total_documents = len(document_data)

    # add data to graph
    graph = DataGraph()
    for data in document_data:
        graph.add_somef_data(data)

    # add keyword data to graph
    # for data in keyword_data:
    #     graph.add_data(data, keyword_schema, keyword_prefixes)

    # search through graph to add the description keyword data
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
            str(keyword) for _, _, keyword in graph.g.triples((software_id, SD.keyword, None))
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
    graph.add_data(all_keyword_data_list, keyword_schema, keyword_prefixes)

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

    graph.add_data(all_relationships_list, keyword_in_software_schema, keyword_prefixes)

    # but we'll have to make 3 calls for the relationships (one for each type)
    graph.add_data(all_relationships_list, description_keyword_relationship_schema, keyword_prefixes)
    graph.add_data(all_relationships_list, title_keyword_relationship_schema, keyword_prefixes)
    graph.add_data(all_relationships_list, keyword_relationship_schema, keyword_prefixes)



    global_data = {
        "totalSoftwareCount": total_documents
    }

    graph.add_data(global_data, global_schema, global_prefixes)

    with open(graph_out, "wb") as out_file:
        out_file.write(graph.g.serialize(format=format))


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
    graph_in = get_config()["endpoint"]
    sparql = SPARQLWrapper(graph_in)

    keywords = [keyword.lower() for keyword in keywords]
    if method == "keyword":
        keywords = get_all_keywords(keywords)

    if method == "description":
        # first, get the global document count

        sparql.setQuery(get_global_doc_count)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()['results']['bindings']
        assert(len(results) == 1)
        doc_count = float(results[0]['doc_count']['value'])
    else:
        doc_count = 0

    print(keywords)
    # first, get all of the keywords and their frequencies
    keyword_idfs = {}
    for keyword in keywords:
        if method == "description":
            query_string = get_description_keyword.format(keyword=keyword)
        else:
            assert(method=="keyword")
            query_string = get_keyword.format(keyword=keyword)

        sparql.setQuery(query_string)
        print(query_string)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()['results']['bindings']

        # there's only 1 or 0 results but this is an easier way of writing that
        for result in results:
            keyword_id = result['obj']['value']

            if method == "description":
                kw_doc_count = float(result['doc_count']['value'])
                keyword_df = kw_doc_count/doc_count
            else:
                assert(method == "keyword")
                keyword_df = float(result['keyword_df_value'])

            keyword_idf = -1 * math.log(keyword_df, math.e)
            keyword_idfs[keyword_id] = keyword_idf

    # now, get the documents that match these keywords
    all_results = {}
    for keyword_id, keyword_idf in keyword_idfs.items():
        if method == "description":
            query_string = get_document_from_description_kw\
                .format(keyword_id=keyword_id)
        else:
            query_string = get_keyword_matches.format(keyword_id=keyword_id)

        sparql.setQuery(query_string)
        # print(query_string)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()

        print(f"keyword: {keyword_id}, idf: {keyword_idf}")

        for result in results['results']['bindings']:
            obj_id = result['obj']['value']
            if method == "description":
                keyword_count = float(result['kw_count']['value'])
                doc_length = float(result['doc_length']['value'])
                keyword_tf = keyword_count / doc_length
            else:
                assert(method == "keyword")
                keyword_tf = 1/float(result['keyword_count'])

            keyword_tf_idf = keyword_tf * keyword_idf

            if obj_id not in all_results:
                all_results[obj_id] = {
                    "tf_idf": 0,
                    "matches": 0
                }

            all_results[obj_id]["tf_idf"] += keyword_tf_idf
            all_results[obj_id]["matches"] += 1

    tf_idf_results = [{"obj_id": obj_id, "matches": value["matches"], "tf_idf": value["tf_idf"]}
                      for obj_id, value in all_results.items()]

    tf_idf_results.sort(key=lambda obj: (obj["matches"], obj["tf_idf"]), reverse=True)

    for index, result in enumerate(tf_idf_results):
        if index >= 20:
            break
        print(result)


def run_describe(iri):
    graph_in = get_config()["endpoint"]
    sparql = SPARQLWrapper(graph_in)
    query_string = describe_iri.format(iri=iri)
    print(query_string)
    sparql.setQuery(query_string)
    sparql.setReturnFormat(SPARQL_JSON)
    result = sparql.query().convert()
    print(result.serialize(format="turtle").decode("utf-8"))
