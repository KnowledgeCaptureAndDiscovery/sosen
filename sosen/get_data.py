import json
import requests
from somef import cli as somef_cli

def get_zenodo_data(query):
    zenodo_api_base = 'https://zenodo.org/api'

    total_count = -1
    output_results = {}

    zenodo_max_api_call = 10000
    query_size = zenodo_max_api_call
    for is_forwards in [True, False]:
        if not is_forwards:
            if total_count < zenodo_max_api_call:
                break
            else:
                query_size = min(total_count - zenodo_max_api_call, zenodo_max_api_call)

        response = requests.get(
            f"{zenodo_api_base}/records",
            params={
                'q': query,
                'size': query_size,
                'type': 'software',
                'page': 1,
                'sort': 'mostrecent' if is_forwards else '-mostrecent'
            },
            headers={
                'Accept': "application/vnd.zenodo.v1+json"
            }
        )
        data_out = response.json()
        if "message" in data_out:
            print(f"error with request: {response.request.path_url}")
            print(data_out["message"])
            break

        results = data_out["hits"]["hits"]
        total_count = data_out["hits"]["total"]

        print(f"got {min(query_size, total_count)} results from {'asc' if is_forwards else 'desc'} search")

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

    with open("test_zenodo_results.json", "w") as test_out:
        json.dump(output_results, test_out)

    return output_results