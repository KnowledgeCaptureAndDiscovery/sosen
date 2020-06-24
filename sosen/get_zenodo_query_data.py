import requests
from rdflib import Namespace
from .schema.software_schema import software_prefixes
from SPARQLWrapper import SPARQLWrapper, JSON
import json

SD = Namespace(software_prefixes["sd"])


def get_zenodo_query_data(query, sparql=None):
    zenodo_api_base = 'https://zenodo.org/api'
    page_size = 20 if sparql is None else 40

    output_dois = []
    page_index = 1
    should_continue = True
    while should_continue:
        response = requests.get(
            f"{zenodo_api_base}/records",
            params={
                'q': query,
                'size': page_size,
                'type': 'software',
                'page': page_index,
                'sort': 'bestmatch'
            },
            headers={
                'Accept': "application/vnd.zenodo.v1+json"
            }
        )
        data_out = response.json()
        if "message" in data_out:
            print(f"error with request: {response.request.path_url}")
            print(data_out["message"])
            return None

        results = data_out["hits"]["hits"]

        def doi_in_graph(doi):
            sparql.setQuery("""
                PREFIX sd: <https://w3id.org/okn/o/sd#>
                SELECT ?subject
                WHERE {{
                  ?subject sd:identifier "{doi}" .
                }}
                LIMIT 1
            """.format(doi=doi))
            sparql.setReturnFormat(JSON)
            query_result = sparql.query().convert()

            print(json.dumps(query_result))

            return len(query_result["results"]["bindings"]) == 1

        for result in results:
            if "conceptdoi" in result:
                doi = result["conceptdoi"]
            else:
                doi = result["doi"]

            # if no graph provided, just add the doi
            if sparql is None:
                output_dois.append(doi)
            # if it is in the graph, add it
            elif doi_in_graph(doi):
                print("DOI in graph")
                output_dois.append(doi)
            # otherwise, we just skip the doi
            else:
                print(f"DOI {doi} was not present in the graph")

            # we should break if the length is enough or if there are no more pages left in the query
            if len(output_dois) >= 20:
                assert(len(output_dois) == 20)
                should_continue = False
                break


        if "next" not in data_out["links"]:
            should_continue = False

        page_index += 1

    return output_dois