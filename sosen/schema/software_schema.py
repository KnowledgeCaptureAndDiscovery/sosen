from .schema_prefixes import schema, sd, xsd, obj, sosen, rdfs

software_prefixes = {
    "schema": schema,
    "sd": sd,
    "xsd": xsd,
    "obj": obj,
    "sosen": sosen,
    "rdfs": rdfs
}

# this goes down here to resolve what would otherwise be a circular dependency
from .keyword_schema import keyword_id_format

somef_software_schema = {
    # class and id
    "@class": "sd:Software",
    "@id": {
        "@format": "obj:Software/{name}",
        "name": ["fullName", "excerpt"]
    },
    # data from SoMEF
    "sd:description": [ # add in zenodo description
        {
            "@path": ["description", "excerpt"],
            "@type": "xsd:string"
        },
        {
            "@path": ["issues", "excerpt"],
            "@type": "xsd:string"
        },
        {
            "@path": ["zenodo_data", "metadata", "description"],
            "@type": "xsd:string"
        }
    ],
    "sd:referencePublication": {
        "@path": ["citation", "excerpt"],
        "@type": "xsd:string"
    },
    # todo: add in citation separately from zenodo as sd:citation
    "sd:hasInstallationInstructions": {
        "@path": ["installation", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:executionInstructions": [
        {
            "@path": ["run", "excerpt"],
            "@type": "xsd:string"
        },
        {
            "@path": ["invocation", "excerpt"],
            "@type": "xsd:string"
        }
    ],
    "sd:hasUsageNotes": {
        "@path": ["usage", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:downloadUrl": {
        "@path": ["downloadUrl", "excerpt"],
        "@type": "xsd:anyURI"
    },
    "sd:downloadInstructions":
    {
        "@path": ["download", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:softwareRequirements": {
        "@path": ["requirement", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:contactDetails": {
        "@path": ["contact", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:contributionInstructions": {
        "@path": ["contributor", "excerpt"],
        "@type": "xsd:string"
    },
    # issues was moved in with sd:description
    "sd:supportDetails": {
        "@path": ["support", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:name": [
        {
            "@path": ["fullName", "excerpt"],
            "@type": "xsd:string"
        },
        {
            "@path": ["zenodo_data", "metadata", "title"],
            "@type": "xsd:string"
        }
    ],
    "sd:license": {
        "@path": ["license", "excerpt", "url"],
        "@type": "xsd:anyURI"
    },
    # link to the keyword, which will be generated separately
    "sd:keyword": {
        "@path": ["topics", "excerpt"],
        "@type": "xsd:string"
    },
    "sd:doi": {
        "@required": True,
        "@path": ["zenodo_data", "conceptdoi"],
        "@type": "xsd:string"
    },
    "sd:identifier": [
        {
            "@path": ["zenodo_data", "doi"],
            "@type": "xsd:string"
        },
        {
            "@path": ["zenodo_data", "conceptdoi"],
            "@type": "xsd:string"
        }
    ],
    "sd:issueTracker": {
        "@value": {
            "@format": "https://github.com/{fullName}/issues",
            "fullName": ["fullName", "excerpt"]
        },
        "@type": "xsd:anyURI"
    },
    "sd:readme": {
        "@path": ["readme_url", "excerpt"],
        "@type": "xsd:anyURI"
    },
    "sd:hasSourceCode": {
        "@class": "sd:SourceCode",
        "@id": {
            "@format": "obj:SoftwareSource/{name}",
            "name": ["fullName", "excerpt"]
        },
        "sd:codeRepository": {
            "@path": ["codeRepository", "excerpt"],
            "@type": "xsd:anyURI"
        },
        "sd:programmingLanguage": {
            "@path": ["languages", "excerpt"],
            "@type": "xsd:string"
        }
    },
    "sd:author": {
        "@class": "schema:Person",
        "@id": {
            "@format": "obj:Person/{name}",
            "name": ["owner", "excerpt"]
        },
        "sd:additionalName": {
            "@path": ["owner", "excerpt"],
            "@type": "schema:Text"
        }
    },
    "sd:hasVersion": {
        "@class": "sd:SoftwareVersion",
        "@id": {
            "@format": "obj:SoftwareVersion/{name}/{tag_name}",
            "tag_name": ["releases", "excerpt", "tag_name"],
            "name": ["fullName", "excerpt"]
        },
        # "sd:author": {
        #     "@class": "schema:Person",
        #     "@id": {
        #         "@format": "obj:Person/{name}",
        #         "name": ["releases", "excerpt", "author_name"]
        #     },
        #     "sd:additionalName": {
        #         "@path": ["releases", "excerpt", "author_name"],
        #         "@type": "xsd:string"
        #     }
        # },
        "sd:hasVersionId": {
            "@path": ["releases", "excerpt", "tag_name"],
            "@type": "xsd:string"
        },
        "sd:description": {
            "@path": ["releases", "excerpt", "body"],
            "@type": "xsd:string"
        },
        "sd:downloadUrl": [
            {
                "@path": ["releases", "excerpt", "tarball_url"],
                "@type": "xsd:anyURI"
            },
            {
                "@path": ["releases", "excerpt", "zipball_url"],
                "@type": "xsd:anyURI"
            },
            {
                "@path": ["releases", "excerpt", "html_url"],
                "@type": "xsd:anyURI"
            }
        ]
    }
}