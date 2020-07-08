from .schema_prefixes import xsd, obj, sosen

global_prefixes = {
    "xsd": xsd,
    "obj": obj,
    "sosen": sosen
}

global_schema = {
    "@id": "obj:Global",
    "@class": "sosen:Global",
    "sosen:totalSoftwareCount": {
        "@path": "totalSoftwareCount",
        "@type": "xsd:integer"
    }
}