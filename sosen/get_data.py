import json
import requests
from somef import cli as somef_cli

def get_zenodo_data(query):
    zenodo_api_base = 'https://zenodo.org/api'
    query_size = 10
    index = 0
    # initialize it big enough to run once
    total_count = query_size + 1

    output_results = {}

    while query_size * index < total_count:
        response = requests.get(
            f"{zenodo_api_base}/records",
            params={
                'q': query,
                'size': query_size,
                'type': 'software',
                'page': index + 1,
            }
        )
        data_out = response.json()

        results = data_out["hits"]["hits"]
        total_count = data_out["hits"]["total"]

        def get_github_url(result):
            try:
                metadata = result['metadata']
                assert ('related_identifiers' in metadata)
                related_identifiers = metadata['related_identifiers']
                for identifier in related_identifiers:
                    if identifier['relation'] == 'isSupplementTo':
                        github_base_url = 'https://github.com/'
                        github_url = identifier['identifier']
                        assert (github_base_url in github_url)
                        # now, process the URL
                        _, _, path = github_url.partition(github_base_url)
                        path_components = path.split('/', 2)

                        return github_base_url + "/".join(path_components[:2])
            except AssertionError:
                pass

            return None

        processed_results = ((result, get_github_url(result)) for result in results)
        output_results.update({result["id"]: {"github_url": github_url, "zenodo_data": result}
                               for result, github_url in processed_results if github_url is not None})
        index += 1

    with open("test_zenodo_results.json", "w") as test_out:
        json.dump(output_results, test_out)

    return output_results