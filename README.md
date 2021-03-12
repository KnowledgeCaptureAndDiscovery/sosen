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
SOSEN currently works against an endpoint where the TTL files from this repository are loaded.
Unfortunately, we cannot ensure the long term accessibility of this endpoint, and hence we provide the RDF dumps.
If the endpoint is not available, you can load the provided data in a local one and change it in the notebooks (look in the first lines for the `configure` command). Replacing the URL should be sufficient for ensuring SOSEN will work.

# Example queries

## Basic statistics
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



