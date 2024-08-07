# SoSEn
Repository for the Software Search Engine (SoSEn)

# Search
See an example [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/KnowledgeCaptureAndDiscovery/sosen/master?filepath=search.ipynb)

# Installation instructions

First, install the requirements.
Then, you'll need to configure SoMEF with

```somef configure```

Next, configure sosen with

```python -m sosen configure```

# Recreate the SOSEN-KG
SOMEF continuously evolves, improving metadata extraction, extracting more metadata categories, etc. Therefore, it's recommendable to re-create the SOSEN-KG when SOMEF does a new release. 

To re-run the metadata extraction and KG creation pipeline, just run:

```
python -m sosen scrape --all -g graph_out.ttl -k keywords_out.ttl -t 0.8 -d somef_cache.json -c zenodo_cache.json
```

The graph will be stored in `graph_out.ttl`, and the keywords in `keywords_out.ttl`. This process may take several hours to finish. 

# Search

There are currently two methods for search: Description-Based search and Title-based search

Both methods extract keywords from the description (or title)
of the software component. Given a query string, the string is
broken up into keywords. Then, we match each
keyword to an extracted keyword in the description of
a software. Every Software that matches at least one
keyword is returned. The results are ranked in descending order
of how many what proportion of the keywords in the query
were in the description of the software. Because there
will be many results which match the same keywords, ties
are then broken by TF-IDF. Each keyword in the query
string is assigned an IDF (Inverse Document Frequency) score, which is given by

```
log(\#{software objects})/(\#{software objects with keyword in description})
```

Further, each keyword within a document is assigned a TF
(Term Frequency) score, which is given by

```
\#{keyword used in description}/\#{total keywords in description}
```
These two numbers are multiplied in order to obtain the TF-IDF score
of a keyword for a particular document. Then, the TF-IDF scores
of all keywords matching a given document are added up
to give an overall score for the document. 

# Running tests
To run the unit tests, run

```python -m unittest test```

# Disclaimer
SOSEN currently works against an endpoint where the TTL files from this repository are loaded (`https://sosen.linkeddata.es/`). To test the endpoint, a sample query may be performed:
```
curl https://sosen.linkeddata.es/sosen -X POST --data 'query=SELECT+%3Fp+(count+(distinct+%3Fsoft)+as+%3Ftotal)%0AWHERE+%7B%0A++%3Fsoft+a+%3Chttps%3A%2F%2Fw3id.org%2Fokn%2Fo%2Fsd%23Software%3E.%0A++%3Fsoft+%3Fp+%3Fv%0A%7Dgroup+by+%3Fp' -H 'Accept: application/sparql-results+json,*/*;q=0.9'
```

Unfortunately, we cannot ensure the long term accessibility of this endpoint, and hence we provide the RDF dumps.
If the endpoint is not available, you can load the provided data in a local one and change the right field in the notebooks (look in the first lines for the `configure` command). Replacing the URL should be sufficient for ensuring the right responses from SOSEN.

# Example queries

## Basic queries
Let's start by extracting some basic metadata from the SOSEN graph. For example, how many software entries have a description?

```
SELECT (count (distinct ?b) as ?total)
WHERE {
?b a <https://w3id.org/okn/o/sd#Software> .
?b <https://w3id.org/okn/o/sd#description> ?c.
}
```
Which results in 12067. You can change `description` by any of the other metadata categories we have currently available in the graph:
```
author, readme, downloadUrl, hasVersion, description, name, license, issueTracker, hasSourceCode, keywords, doi,hasInstallationInstructions, softwareRequirements, executionInstructions, contactDetails, referencePublication,hasUsageNotes, contributionInstructions, downloadInstructions, supportDetails
```

Bear in mind that if you want to do operations with keywords, you need to use the sosen-specific namespace `https://w3id.org/okn/o/sosen#`. This would be used for the following properties:

```
hasKeyword, titleKeywordCount, hasDescriptionKeyword, keywordCount, descriptionKeywordCount, hasTitleKeyword

```
## Full description of a software entry
Just replace your target software after `https://w3id.org/okn/i/Software/` (user/repo) and you'll obtain all the available metadata for that software entry in SOSEN. For example, for `dgarijo/Widoco`:

```
SELECT distinct ?b ?c
WHERE {
<https://w3id.org/okn/i/Software/dgarijo/Widoco> ?b ?c.
}
```
The results are ommitted for simplicity.

## Search by keyword
This case is tested best with the notebook we have prepared above. The notebook makes use of a query for calculating dynamically a TF-IDF score of the keywords inserted, returning the closest results.

## What are the available versions of a software entry?
We capture the hierarchical relationship between a software and its different releases, including their DOIs and descriptions. For example, for the software entry above:

```
SELECT distinct ?c
WHERE {
<https://w3id.org/okn/i/Software/dgarijo/Widoco> <https://w3id.org/okn/o/sd#hasVersion> ?version.
  ?version <https://w3id.org/okn/o/sd#doi> ?c
}
```
would return a list of the DOIs associated with all the different releases of WIDOCO in Zenodo.

## Retrieving software by author id:
One can also retrieve entries authored by a GitHub id user. For example, for the user `dgarijo`

```
SELECT distinct ?soft
WHERE {
?soft a <https://w3id.org/okn/o/sd#Software> .
?soft <https://w3id.org/okn/o/sd#author>/<https://w3id.org/okn/o/sd#additionalName> "dgarijo".
}
```

Which returns:

```
<https://w3id.org/okn/i/Software/dgarijo/Widoco>
<https://w3id.org/okn/i/Software/dgarijo/DataNarratives>
<https://w3id.org/okn/i/Software/dgarijo/FragFlow>
```
If now we want to retrieve their license, we just need to issue the following query:

```
SELECT distinct ?soft ?l
WHERE {
?soft a <https://w3id.org/okn/o/sd#Software> .
?soft <https://w3id.org/okn/o/sd#author>/<https://w3id.org/okn/o/sd#additionalName> "dgarijo".
?soft <https://w3id.org/okn/o/sd#license> ?l
}
```
which would return 

```
<https://w3id.org/okn/i/Software/dgarijo/DataNarratives>
	
"https://api.github.com/licenses/apache-2.0"^^xsd:anyURI
```
Meaning that some of these software entries do not have a license (as it is the case of FragFlow), or that the license was not one of the common licenses used in GitHub (as it's the case of WIDOCO)

## SOSEN in numbers:
The following queries may be slow, but will retrieve property coverage in SOSEN:

```
SELECT ?p (count (distinct ?soft) as ?total)
WHERE {
  ?soft a <https://w3id.org/okn/o/sd#Software>.
  ?soft ?p ?v
}group by ?p
```
To get the distribution of the programming languages in SOSEN:

```
SELECT ?pl (count (distinct ?soft) as ?total)
WHERE {
  ?soft <https://w3id.org/okn/o/sd#programmingLanguage> ?pl
}group by ?pl order by desc(?total)
```

Finally, number of repositories with more than one version:

```
SELECT (count (distinct ?s) as ?total)
WHERE {
 ?s <https://w3id.org/okn/o/sd#hasVersion> ?v.
 ?s <https://w3id.org/okn/o/sd#hasVersion> ?w
  filter(?v!=?w) 
}
```
