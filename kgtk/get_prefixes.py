# from sosen.schema.schema_prefixes import schema, sd, xsd, obj, sosen, rdfs
# this is a hack... just copied from the file.
# todo: resolve later once sosen is really a module
from rdflib import XSD, RDFS

schema =  "https://schema.org/"
sd = "https://w3id.org/okn/o/sd#"
xsd = str(XSD)
obj = "https://w3id.org/okn/o/i/"
sosen = "http://example.org/sosen#"
rdfs = str(RDFS)

prefixes_dict = {
    "schema": schema,
    "sd": sd,
    "xsd": xsd,
    "obj": obj,
    "sosen": sosen,
    "rdfs": rdfs
}

print("node1\tlabel\tnode2")

for key, value in prefixes_dict.items():
    print(f"{key}\tprefix_expansion\t\"{value}\"")