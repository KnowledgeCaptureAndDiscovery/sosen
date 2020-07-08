# get_keyword_matches = """PREFIX sd: <https://w3id.org/okn/o/sd#>
# SELECT ?obj (COUNT(*) as ?keyword_count) {{
# ?obj sd:hasKeyword ?keyword .
#     {{
#         SELECT ?obj WHERE {{
#             ?obj a sd:Software .
#             ?obj sd:hasKeyword <{keyword_id}> .
#         }}
#     }}
# }}
# GROUP BY ?obj
# """
#
# get_keyword = """
# PREFIX sd: <https://w3id.org/okn/o/sd#>
# SELECT ?keyword_id ?keyword_df {{
#     ?keyword_id a sd:Keyword .
#     ?keyword_id sd:keyword "{keyword}" .
#     ?keyword_id sd:documentFrequency ?keyword_df
# }}
# """

def get_keyword(option):
    options = {
        "description": "sosen:descriptionInCount",
        "title": "sosen:titleInCount",
        "keyword": "sosen:keywordInCount"
    }

    in_name = options[option]

    return """
PREFIX sosen: <http://example.org/sosen#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?obj ?doc_count {{
  ?obj a sosen:Keyword .
  ?obj rdfs:label "{keyword}" .
  ?obj """+in_name+""" ?doc_count
}}
"""


def get_document_from_kw(option):
    options = {
        "description": ("sosen:descriptionKeywordCount", "sosen:descriptionCount"),
        "title": ("sosen:titleKeywordCount", "sosen:titleCount"),
        "keyword": ("sosen:keywordCount", "sosen:keywordCount")
    }

    total_count, kw_count = options[option]

    return """
PREFIX sosen: <http://example.org/sosen#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sd: <https://w3id.org/okn/o/sd#>

SELECT ?obj ?kw_count ?doc_length {{
  ?obj a sd:Software .
  ?obj """+total_count+""" ?doc_length .
  ?kw_relationship sosen:hasSoftware ?obj .
  ?kw_relationship sosen:hasKeyword <{keyword_id}> .
  ?kw_relationship """+kw_count+""" ?kw_count
}}
"""

get_global_doc_count = """
PREFIX sosen: <http://example.org/sosen#>

SELECT ?doc_count {
  ?obj a sosen:Global .
  ?obj sosen:totalSoftwareCount ?doc_count
}
"""

describe_iri = """DESCRIBE <{iri}>"""