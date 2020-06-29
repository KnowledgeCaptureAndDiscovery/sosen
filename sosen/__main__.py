import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from .cli import run_scrape, get_data

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
@click.option(
    '--data_dict',
    '-d',
    type=click.Path(),
    required=False
)
def run(**kwargs):
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
@click.option(
    "--graph_in",
    "-g",
    type=str,
    help="link to the SPARQL endpoint"
)
def get_data(**kwargs):
    get_data(**kwargs)


if __name__ == "__main__":
    cli()
