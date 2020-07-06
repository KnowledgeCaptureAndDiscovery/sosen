from .software_schema import software_prefixes
from .schema_prefixes import obj, xsd, sosen, rdfs

keyword_prefixes = {
    "obj": obj,
    "xsd": xsd,
    "sosen": sosen,
    "rdfs": rdfs
}

keyword_id_format = "obj:Keyword/{keyword}"

keyword_schema = {
    "@id": {
        "@format": keyword_id_format,
        "keyword": "keyword"
    },
    "@class": "sosen:Keyword",
    "rdfs:label": {
        "@path": "keyword",
        "@type": "xsd:string"
    },
    "sosen:documentCount": {
        "@path": "documentCount",
        "@type": "xsd:integer"
    }
}
description_keyword_in_software_schema = {
    "@class": "sd:software",
    "@id": {
        "@path": "id"
    },
    "sd:hasDescriptionKeyword": {
        "@class": "sosen:KeywordRelationship",
        "@id": {
            "@format": "{softwareName}/KeywordRelationship/{keyword}",
            "softwareName": ["id"],
            "keyword": ["keywords", "label"]
        },
        "sosen:descriptionCount": {
            "@path": ["keywords", "count"],
            "@type": "xsd:integer"
        },
        "sosen:keyword": {
            "@id": {
                "@format": keyword_id_format,
                "keyword": ["keywords", "label"]
            }
        }
    },
    "sd:descriptionKeywordCount": {
        "@path": "keywordCount",
        "@value": "xsd:integer",
    }
}