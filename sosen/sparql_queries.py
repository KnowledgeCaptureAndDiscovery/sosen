get_keyword_matches = """PREFIX sd: <https://w3id.org/okn/o/sd#>
SELECT ?obj (COUNT(*) as ?keyword_count) {{
?obj sd:hasKeyword ?keyword .
    {{
        SELECT ?obj WHERE {{
            ?obj a sd:Software .
            ?obj sd:hasKeyword <{keyword_id}> .
        }}
    }}
}}
GROUP BY ?obj
"""

get_keyword = """
PREFIX sd: <https://w3id.org/okn/o/sd#>
SELECT ?keyword_id ?keyword_df {{
    ?keyword_id a sd:Keyword .
    ?keyword_id sd:keyword "{keyword}" .
    ?keyword_id sd:documentFrequency ?keyword_df
}}
"""

get_description_keyword = """
PREFIX sosen: <http://example.org/sosen#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?obj ?doc_count {{
  ?obj a sosen:Keyword .
  ?obj rdfs:label "{keyword}" .
  ?obj sosen:documentInCount ?doc_count
}}
"""

get_document_from_description_kw = """
PREFIX sosen: <http://example.org/sosen#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sd: <https://w3id.org/okn/o/sd#>

SELECT ?obj ?kw_count ?doc_length {{
  ?obj a sd:Software .
  ?obj sosen:descriptionKeywordCount ?doc_length .
  ?kw_relationship sosen:hasSoftware ?obj .
  ?kw_relationship sosen:hasKeyword <{keyword_id}>
  ?kw_relationship sosen:descriptionCount ?kw_count
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