import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from .cli import run_scrape, run_get_data, run_search, run_describe
from .config import configure as configure_sosen, get_config, SosenConfigurationException, get_defaults

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
    '--zenodo_in',
    '-z',
    type=click.Path(exists=True),
    help="Path to a Zenodo Cache .json file. The program will not make calls to Zenodo and instead use this"
)
@click.option(
    '--graph_out',
    '-g',
    type=click.Path(),
    help="Path to the output knowledge graph file"
)
@click.option(
    '--keyword_out',
    '-k',
    type=click.Path(),
    help="Path to the output knowledge graph file for keywords"
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
    '--data_dict',
    '-d',
    type=click.Path(),
    required=False,
    help="The path to a dictionary that will be used both to load and save outputs from SoMEF"
)
@click.option(
    '--zenodo_cache',
    '-c',
    type=click.Path(),
    required=False,
    help="Path to a .json file which will be used to save data from Zenodo"
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



tabulate_format_kwargs = click.option(
    "--format",
    "-f",
    type=click.Choice(["github", "latex"]),
    required=False,
    default="github"
)

@cli.command(help="keyword search")
@click.argument(
    "keywords",
    type=str,
    nargs=-1
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["description", "keyword", "title"]),
    required=False,
    default="description"
)
@tabulate_format_kwargs
def search(**kwargs):
    run_search(**kwargs)

@cli.command(help="Configure sosen. You will be prompted for information")
def configure():
    try:
        defaults = get_config()
    except SosenConfigurationException:
        defaults = get_defaults()

    endpoint = click.prompt("SPARQL Endpoint", default=defaults["endpoint"])
    object_prefix = click.prompt("Object Prefix", default=defaults["object_prefix"])

    configure_sosen(endpoint=endpoint, object_prefix=object_prefix)

@cli.command(help="describe an object")
@click.argument("iris",
                type=str,
                nargs=-1)
@tabulate_format_kwargs
def describe(**kwargs):
    run_describe(**kwargs)


def get_input_with_constraint(message, constraint):
    while True:
        user_input = input(message)
        if constraint(user_input):
            return user_input


def get_input_from_choices(message, choices):
    def choice_constraint(choice):
        return choice in choices

    return get_input_with_constraint(message, choice_constraint)

def get_choice(message, choices_dict):
    reverse_dict = {
        value: key for key, values in choices_dict.items() for value in values
    }
    choices = [value for value in reverse_dict.keys()]
    choice = get_input_from_choices(message, choices)

    return reverse_dict[choice]

@cli.command(help="run interactively")
def interactive():

    search_results = None

    while True:
        choice = get_choice(
            "Choose an action (search/describe/quit):> ",
            {
                "search": [
                    "search",
                    "s"
                ],
                "describe": [
                    "describe",
                    "d"
                ],
                "quit": [
                    "quit",
                    "q"
                ]
            }
        )

        if choice == "quit":
            return
        elif choice == "describe":
            print("Enter a space-separated list of URIs")
            if search_results is not None:
                print("Alternatively, enter numbers 1-20, referring to the results of the previous search")

            choice = get_input_with_constraint(">", lambda x: True)

            def decode_uri(uri):
                try:
                    assert(search_results is not None)
                    index = int(uri)
                    assert(1 <= index <= 20)
                    return search_results[index-1]
                except (ValueError, KeyError, AssertionError):
                    return uri

            uris = [decode_uri(uri) for uri in choice.split(" ")]

            run_describe(iris=uris)

        elif choice == "search":
            method = get_choice("Which method (description/keyword/title)?> ",
                                    {
                                        "description": ["description", "d"],
                                        "keyword": ["keyword", "k"],
                                        "title": ["title", "t"]
                                    }
                                )

            query = get_input_with_constraint("what is your query?> ", lambda x: True)
            keywords = query.split(" ")

            search_results = run_search(keywords=keywords, method=method)




if __name__ == "__main__":
    cli()

