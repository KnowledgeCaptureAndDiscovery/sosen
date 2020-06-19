import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
import requests
import json
from somef import cli as somef_cli
from .data_to_graph import DataGraph
from .get_data import get_zenodo_data
import math

print("test")

@click.group(context_settings={'help_option_names':['-h','--help']})
def cli():
    print("SoSEn Command Line Interface")


@cli.command(help='run kg')
@optgroup.group('Input', cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option(
    '--queries',
    '-q',
    type=click.Path(exists=True),
    help="Path to a list of queries to use with the zenodo API"
)
@optgroup.option(
    '--all',
    '-a',
    is_flag=True,
    help="Run a blank search and get all inputs"
)
@optgroup.option(
    '--zenodo_data',
    '-z',
    type=click.Path(exists=True),
    help="for debug"
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
@click.option(
    '--format',
    '-f',
    type=click.Choice(["json-ld", "turtle"]),
    required=False,
    default="turtle"
)
def run(queries, all, graph_out, zenodo_data, threshold, format):
    print("running")
    if not zenodo_data:
        if all:
            queries = {""}
        else:
            with open(queries, "r") as in_handle:
                # get all of the queries
                queries = {stripped_line for stripped_line in
                           (line.rstrip("\n") for line in in_handle)
                           # if len(stripped_line) > 0
                           }

        print(queries)
        # get the data from zenodo for each
        data_and_urls = (get_zenodo_data(query) for query in queries)

        # flatten it all into one object and use a dict to guarantee uniqueness
        data_and_urls_flattened = {}
        total_len = 0
        for dict_obj in data_and_urls:
            total_len += len(dict_obj)
            data_and_urls_flattened.update(dict_obj)
            print(f"total len: {len(data_and_urls_flattened)}, total gathered: {total_len}, repeats: {total_len - len(data_and_urls_flattened)}")

    else:
        with open(zenodo_data, "r") as in_file:
            data_and_urls_flattened = json.load(in_file)


    # save the data and urls flattened object
    with open(graph_out + ".data_and_urls.json", "w") as out_file:
        json.dump(data_and_urls_flattened, out_file)

    # make sure that the github urls are all unique, too
    github_urls = {data["github_url"] for data in data_and_urls_flattened.values()}

    # get the data from the cli
    github_urls_and_data = ((github_url, somef_cli.cli_get_data(threshold, repo_url=github_url)) for github_url in github_urls)
    cli_data = {github_url: data for github_url, data in github_urls_and_data if data is not None}

    graph = DataGraph()

    filtered_data = (data for data in data_and_urls_flattened.values() if data["github_url"] in cli_data)

    for data in filtered_data:
        graph.add_somef_data({**cli_data[data["github_url"]], "zenodo_data": data["zenodo_data"]})

    with open(graph_out, "wb") as out_file:
        out_file.write(graph.g.serialize(format=format))


if __name__ == "__main__":
    cli()
