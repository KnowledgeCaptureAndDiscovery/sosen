import json
import requests
import time
from somef import cli as somef_cli

def zenodo_get(*args, **kwargs):
    backoff_rate = 2
    backoff = 1
    while True:
        response = requests.get(*args, **kwargs)
        data = response.json()

        if "message" in data:
            if "status" in data and data["status"] == 429:
                print(f"rate limited. sleeping for {backoff} seconds")
                time.sleep(backoff)
                backoff *= backoff_rate
            else:
                print(f"other error in the data for {response.request.path_url}")
                print(data)
        else:
            return data

def get_zenodo_data(query, recursive=True):
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

        all_versions = {}

        if not recursive:
            all_versions["all_versions"] = True

        print("calling zenodo api")
        zenodo_call_time = time.time()
        data_out = zenodo_get(
            f"{zenodo_api_base}/records",
            params={
                'q': query,
                'size': query_size,
                'type': 'software',
                'page': 1,
                'sort': 'mostrecent' if is_forwards else '-mostrecent',
                **all_versions
            },
            headers={
                'Accept': "application/vnd.zenodo.v1+json"
            }
        )
        print(f"got result from zenodo api in {time.time() - zenodo_call_time} seconds")

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
                        path_components = path.split('/')

                        return github_base_url + "/".join(path_components[:2]), path_components[-1]
            except AssertionError:
                pass

            return None

        for result in results:
            github_url_result = get_github_url(result)
            result_id = result["id"]
            if github_url_result is not None:
                github_url, github_version = github_url_result

                output_results[result_id] = {
                    "github_url": github_url,
                    "version": github_version,
                    "data": result
                }

                # add the children, too
                if recursive:
                    conceptrecid = result["conceptrecid"]
                    print("doing recursive search")
                    children_data = get_zenodo_data(f"conceptrecid:\"{conceptrecid}\"", recursive=False)
                    output_results.update(children_data)
            else:
                output_results[result_id] = None

                #
                # if github_url not in output_results:
                #     output_results[github_url] = []
                #
                # output_results[github_url].append(
                #     {"version": github_version, "data": result}
                # )


    with open("test_zenodo_results.json", "w") as test_out:
        json.dump(output_results, test_out)

    return output_results