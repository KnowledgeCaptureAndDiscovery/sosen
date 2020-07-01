from .software_schema import software_prefixes

keyword_prefixes = {
    "sd": software_prefixes["sd"],
    "obj": software_prefixes["obj"],
    "xsd": software_prefixes["xsd"]
}

keyword_id_format = "obj:Keyword/{keyword}"

keyword_schema = {
    "@id": {
        "@format": keyword_id_format,
        "keyword": "keyword"
    },
    "@class": "sd:Keyword",
    "sd:keyword": {
        "@path": "keyword",
        "@type": "xsd:string"
    },
    "sd:documentFrequency": {
        "@path": "documentFrequency",
        "@type": "xsd:float"
    }
}