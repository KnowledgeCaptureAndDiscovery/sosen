# SoSEn
Repository for the Software Search Engine (SoSEn)

# Search
See an example [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/KnowledgeCaptureAndDiscovery/sosen/master?filepath=search.ipynb)

# instructions


First, install the requirements.
Then, you'll need to configure SoMEF with

```somef configure```

Next, configure sosen with

```python -m sosen configure```

# Search

There are currently two methods for search

# Description-Based search

This method extracts keywords from the description
of the Software. Given a query string, the string is
broken up into keywords. Then, we match each
keyword to an extracted keyword in the description of
a software. Every Software that matches at least one
keyword is returned. The results are ranked in descending order
of how many what proportion of the keywords in the query
were in the description of the software. Because there
will be many results which match the same keywords, ties
are then broken by TF-IDF. Each keyword in the query
string is assigned an IDF (Inverse Document Frequency) score, which is given by 
log(\#{software objects})/(\#{software objects with keyword in description}).
Further, each keyword within a document is assigned a TF
(Term Frequency) score, which is given by
\#{keyword used in description}/\#{total keywords in description}.
These two numbers are multiplied in order to obtain the TF-IDF score
of a keyword for a particular document. Then, the TF-IDF scores
of all keywords matching a given document are added up
to give an overall score for the document. 

# running tests
To run the unit tests, run

```python -m unittest test```
