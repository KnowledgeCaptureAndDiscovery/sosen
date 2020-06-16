# sosen
Repository for the Software Search Engine (SoSEn)

# instructions

First, install the requirements.
Then, you'll need to configure SoMEF.
Next, create a file with the queries of
Zenodo that you would like to do. It should be
newline-separated, meaning one query on each line.

Then, run

```python -m sosen run -q zenodo_queries.txt -g graph_out.ttl```

This will run the queries listed in
```zenodo_queries.txt``` (restricted to software),
and if the result has a GitHub link, then it will extract
the metadata from GitHub and output it as a Knowledge Graph
to ```graph_out.ttl```