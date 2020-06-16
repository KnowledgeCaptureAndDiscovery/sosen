import click
import requests
import json
from somef import cli as somef_cli
from .data_to_graph import DataGraph
from .get_data import get_zenodo_data

print("test")

@click.group(context_settings={'help_option_names':['-h','--help']})
def cli():
    print("SoSEn Command Line Interface")


@cli.command(help='run kg')
@click.option(
    '--queries',
    '-q',
    type=click.Path(exists=True),
    help="Path to a list of queries to use with the zenodo API",
    required=True
)
@click.option(
    '--graph_out',
    '-g',
    type=click.Path(),
    help="Path to the output knowledge graph file"
)
@click.option(
    '--threshold',
    '-t',
    type=float,
    help="Threshold for SoMEF",
    required=False,
    default=0.8
)
def run(queries, graph_out, threshold):
    print("running")
    with open(queries, "r") as in_handle:
        # get all of the queries
        queries = {stripped_line for stripped_line in
                   (line.rstrip("\n") for line in in_handle)
                   if len(stripped_line) > 1}

    print(queries)
    # get the data from zenodo for each
    data_and_urls = (get_zenodo_data(query) for query in queries)
    # flatten it all into one object and use a dict to guarantee uniqueness
    data_and_urls_flattened = {key: value for data_out in data_and_urls
                               for key, value in data_out.items()}

    # make sure that the github urls are all unique, too
    github_urls = {data["github_url"] for data in data_and_urls_flattened.values()}
    print(github_urls)
    # get the data from the cli
    cli_data = {github_url: somef_cli.cli_get_data(threshold, repo_url=github_url)
                for github_url in github_urls}

    combined_data = [{**cli_data[value["github_url"]], "zenodo_data":value["zenodo_data"]}
                     for value in data_and_urls_flattened.values()]

    graph = DataGraph()
    graph.add_somef_data(combined_data)
    with open(graph_out, "wb") as out_file:
        out_file.write(graph.g.serialize(format="turtle"))


if __name__ == "__main__":
    cli()
