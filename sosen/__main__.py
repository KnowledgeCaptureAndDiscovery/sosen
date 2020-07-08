import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from .cli import run_scrape, run_get_data, run_search, run_describe
from .config import configure as configure_sosen

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
@click.option(
    '--data_dict',
    '-d',
    type=click.Path(),
    required=False
)
def scrape(**kwargs):
    run_scrape(**kwargs)


@cli.command(help="get testing/training data")
@click.option(
    "--queries",
    "-q",
    type=click.Path(exists=True),
    help="Newline-separated file of queries",
    required=True
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output JSON file to save the data to",
    required=True
)
def get_data(**kwargs):
    run_get_data(**kwargs)

@cli.command(help="keyword search")
@click.argument(
    "keywords",
    type=str,
    nargs=-1
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["description", "keyword"]),
    required=False,
    default="description"
)
def search(**kwargs):
    run_search(**kwargs)

@cli.command(help="Configure sosen. You will be prompted for information")
def configure():
    sparql_endpoint = click.prompt("SPARQL Endpoint", default="http://localhost:3030/zenodo")
    configure_sosen(sparql_endpoint)

@cli.command(help="describe an object")
@click.argument("iri",
                type=str)
def describe(**kwargs):
    run_describe(**kwargs)


if __name__ == "__main__":
    cli()

