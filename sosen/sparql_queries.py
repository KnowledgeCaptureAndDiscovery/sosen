import typing
from SPARQLWrapper import JSON as SPARQL_JSON, SPARQLWrapper


def do_query(query: str, sparql: SPARQLWrapper):
    sparql.setQuery(query)
    sparql.setReturnFormat(SPARQL_JSON)
    return sparql.query().convert()['results']['bindings']


def get_global_doc_count(sparql: SPARQLWrapper = None):
    query = """
PREFIX sosen: <http://example.org/sosen#>

SELECT ?doc_count {
  ?obj a sosen:Global .
  ?obj sosen:totalSoftwareCount ?doc_count
}
"""

    if sparql is None:
        return query
    else:
        results = do_query(query, sparql)
        assert (len(results) == 1)
        return float(results[0]['doc_count']['value'])


describe_iri = """DESCRIBE <{iri}>"""


def get_keywords(keywords, method, sparql: SPARQLWrapper = None):
    options = {
        "description": "sosen:descriptionInCount",
        "title": "sosen:titleInCount",
        "keyword": "sosen:keywordInCount"
    }

    in_name = options[method]
    keywords_format = [f"    \"{kw}\"" for kw in keywords]
    keywords_string = "\n".join(keywords_format)

    query = """
PREFIX sosen: <http://example.org/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?obj ?doc_count WHERE {
  ?obj a sosen:Keyword .
  VALUES ?keyword {
""" + keywords_string + """
  } .
  ?obj rdfs:label ?keyword .
  ?obj """ + in_name + """ ?doc_count .
}
LIMIT 10
"""

    print(query)

    if sparql is None:
        return query
    else:
        return do_query(query, sparql)


def get_document_from_kw(keywords, method, sparql: SPARQLWrapper = None):
    options = {
        "description": ("sosen:descriptionKeywordCount", "sosen:descriptionCount"),
        "title": ("sosen:titleKeywordCount", "sosen:titleCount"),
        "keyword": ("sosen:keywordCount", "sosen:keywordCount")
    }

    total_count, kw_count = options[method]

    kw_format_array = [f"    ( <{kw}> {idf} )" for kw, idf in keywords.items()]
    kw_values = "\n".join(kw_format_array)

    query = """
PREFIX sosen: <http://example.org/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>

SELECT ?obj (SUM(?tf_idf) as ?sum_tf_idf) (COUNT(?keyword) as ?matches)
WHERE {
  VALUES (?keyword ?idf) {
""" + kw_values + """
  }
  ?kw_relationship a sosen:KeywordRelationship .
  ?kw_relationship sosen:hasKeyword ?keyword .
  ?kw_relationship """ + kw_count + """ ?kw_count .
  ?kw_relationship sosen:hasSoftware ?obj .
  ?obj """ + total_count + """ ?total_kw_count .
  BIND(?idf * ?kw_count/?total_kw_count as ?tf_idf)
}
GROUP BY ?obj
ORDER BY DESC(?matches) DESC(?sum_tf_idf)
LIMIT 20
"""

    if sparql is None:
        return query
    else:
        return do_query(query, sparql)