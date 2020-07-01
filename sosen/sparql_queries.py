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
