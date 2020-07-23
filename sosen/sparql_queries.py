import typing
from SPARQLWrapper import JSON as SPARQL_JSON, SPARQLWrapper

def get_prop(query, prop, sparql):
    results = do_query(query, sparql)
    # print(results)
    return [result[prop]["value"] for result in results]

def do_query(query: str, sparql: SPARQLWrapper):
    # print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(SPARQL_JSON)
    return sparql.query().convert()['results']['bindings']

def get_software_from_kw(keywords, method, sparql):
    options = {
        "description": (
            "sosen:totalDescriptionInCount",
            "sosen:inDescriptionCount",
            "sosen:descriptionKeywordCount"
        ),
        "title": (
            "sosen:totalTitleInCount",
            "sosen:inTitleCount",
            "sosen:titleKeywordCount"
        ),
        "keyword": (
            "sosen:totalKeywordInCount",
            "sosen:inKeywordCount",
            "sosen:keywordCount"
        )
    }

    total_in_count, in_count, count = options[method]

    kws_string = "\n".join([f"        \"{kw}\"" for kw in keywords])

    big_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>

SELECT ?software (SUM(?tf_idf) as ?sum_tf_idf) (COUNT(?keyword) as ?matches)
WHERE {
  {
    SELECT ?keyword (math:log(?total_doc_count/?doc_count) as ?idf) WHERE {
      {
        SELECT ?total_doc_count WHERE {
          ?global a sosen:Global .
          ?global sosen:totalSoftwareCount ?total_doc_count .
      	}
      }
      ?keyword a sosen:Keyword .
      VALUES ?label {
""" + kws_string + """
      } .
      ?keyword rdfs:label ?label .
      ?keyword """ + total_in_count + """ ?doc_count .
  	}
  }
  ?qualified_kw a sosen:QualifiedKeyword .
  ?qualified_kw sosen:keyword ?keyword .
  ?qualified_kw """ + in_count + """ ?kw_count .
  ?qualified_kw sosen:software ?software .
  ?software """ + count + """ ?total_kw_count .
  BIND(?idf * ?kw_count/?total_kw_count as ?tf_idf)
}
GROUP BY ?software
ORDER BY DESC(?matches) DESC(?sum_tf_idf)
LIMIT 20
"""

    return do_query(big_query, sparql)


def describe_software(iri, sparql):
    description_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?description WHERE {
  <""" + iri + """> sd:description ?description .
  BIND(STRLEN(?description) as ?len) .
}
ORDER BY ?len LIMIT 1
"""

    description = get_prop(description_query, "description", sparql)

    author_name_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?author_name WHERE {
  <""" + iri + """> sd:author/sd:additionalName ?author_name .
}    
"""

    author_name = get_prop(author_name_query, "author_name", sparql)

    language_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?language WHERE {
  <""" + iri + """> sd:hasSourceCode/sd:programmingLanguage ?language .
}
"""

    languages = get_prop(language_query, "language", sparql)

    name_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?name WHERE {
  <""" + iri + """> sd:name ?name .
}    
"""
    name = get_prop(name_query, "name", sparql)

    download_instructions_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?instructions WHERE {
  <""" + iri + """> sd:downloadInstructions ?instructions .
}
"""

    download = get_prop(download_instructions_query, "instructions", sparql)

    license_query = """
PREFIX sosen: <https://w3id.org/okn/o/sosen#>
PREFIX sd: <https://w3id.org/okn/o/sd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX math: <http://www.w3.org/2005/xpath-functions/math#>
PREFIX schema: <http://schema.org/>

SELECT ?license WHERE {
  <""" + iri + """> sd:license ?license .
}"""

    license = get_prop(license_query, "license", sparql)

    return {
        "name": name,
        "author": author_name,
        "description": description,
        "languages": languages,
        "download": download,
        "license": license
    }

def sort_combined(*data):
    # print(data)
    sets = [set(val) for val in data]
    # print(sets)
    if len(data) > 1:
        union = sets[0].intersection(*sets[1:])
    else:
        union = set()

    def sort_by_len(x):
        print(x)
        if len(x) > 0:
            return sorted(x, key=len, reverse=True)
        else:
            return x

    sorted_data = []
    sorted_union = sort_by_len(list(union))

    sorted_data = [
        [
            *sorted_union,
            *sort_by_len(list(x.difference(union)))
        ]
        for x in sets
    ]

    return sorted_data

def compare_softwares(iris, sparql):
    data = [describe_software(iri, sparql) for iri in iris]

    keys = ["name", "author", "description",
            "languages", "download", "license"]

    combined_data = {
        key: [value[key] for value in data]
        for key in keys
    }

    table_data = [
        [key, *sort_combined(*combined_data[key])]
        for key in keys
    ]

    print(table_data)

    return table_data















