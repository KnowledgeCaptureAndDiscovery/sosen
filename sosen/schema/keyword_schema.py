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
    "sosen:descriptionInCount": {
        "@path": "descriptionInCount",
        "@type": "xsd:integer"
    },
    "sosen:titleInCount": {
        "@path": "titleInCount",
        "@type": "xsd:integer"
    },
    "sosen:keywordInCount": {
        "@path": "keywordInCount",
        "@type": "xsd:integer"
    }
}

software_class_id_dict = {
    "@class": "sd:Software",
    "@id": {
        "@path": "id"
    }
}

keyword_in_software_schema = {
    **software_class_id_dict,
    "sosen:hasDescriptionKeyword": {
        "@class": "sosen:Keyword",
        "@id": {
            "@format": keyword_id_format,
            "keyword": ["descriptionKeywords", "label"]
        }
    },
    "sosen:descriptionKeywordCount": {
        "@path": "descriptionKeywordCount",
        "@type": "xsd:integer"
    },
    "sosen:hasTitleKeyword": {
        "@class": "sosen:Keyword",
        "@id": {
            "@format": keyword_id_format,
            "keyword": ["titleKeywords", "label"]
        }
    },
    "sosen:titleKeywordCount": {
        "@path": "titleKeywordCount",
        "@type": "xsd:integer"
    },
    "sosen:hasKeyword": {
        "@class": "sosen:Keyword",
        "@id": {
            "@format": keyword_id_format,
            "keyword": ["keywords", "label"]
        }
    },
    "sosen:keywordCount": {
        "@path": "keywordCount",
        "@type": "xsd:integer"
    },
}


def get_keywords_relationship_schema(option):
    config_options = {
        "description": {
            "keywords_directory": "descriptionKeywords",
            "count_name": "sosen:descriptionCount"
        },
        "keyword": {
            "keywords_directory": "keywords",
            "count_name": "sosen:keywordCount"
        },
        "title": {
            "keywords_directory": "titleKeywords",
            "count_name": "sosen:titleCount"
        }
    }

    config = config_options[option]

    return {
        "@class": "sosen:KeywordRelationship",
        "@id": {
            "@format": "{softwareId}/KeywordRelationship/{keyword}",
            "softwareId": ["id"],
            "keyword": [config["keywords_directory"], "label"]
        },
        config["count_name"]: {
            "@path": [config["keywords_directory"], "count"],
            "@type": "xsd:integer"
        },
        "sosen:hasKeyword": {
            "@id": {
                "@format": keyword_id_format,
                "keyword": [config["keywords_directory"], "label"]
            },
            "@class": "sosen:Keyword"
        },
        "sosen:hasSoftware": software_class_id_dict
    }

description_keyword_relationship_schema = get_keywords_relationship_schema("description")
keyword_relationship_schema = get_keywords_relationship_schema("keyword")
title_keyword_relationship_schema = get_keywords_relationship_schema("title")