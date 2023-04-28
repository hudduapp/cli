from hcli.api.utils import ApiClient
from hcli.utils import config
from hcli.utils.permanent_storage import read_field

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "http://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {token}"},
)


def get_machine_api_client(base_url: str):
    return ApiClient(base_url=base_url, headers={"Authorization": f"Token {token}"})


def get_machines_for_an_app(app_id: str, params: dict = {}):
    has_more = True
    skip = 0
    while has_more:
        res = core_api.request(
            "GET",
            f"organizations/{organization_id}/instances/search?limit=25&skip={skip}&app={app_id}",
            params=params,
        )
        skip += 25

        if len(res["data"]) < 25:
            has_more = False
        for i in res["data"]:
            yield i


def create_machine(
    region: str,
    app: str,
    name: str = None,
    machine_type: str = "us-central",
    disk_size: int = 10,
    meta: dict = {},
):
    region_base_url = config.regions[region]
    machines_api = get_machine_api_client(base_url=region_base_url)

    machines_api.request(
        "POST",
        f"/organizations/{organization_id}/machines",
        body={
            "name": name,
            "app": app,
            "machine_type": machine_type,
            "disk_size": disk_size,
            "meta": meta,
        },
    )


def delete_machine(region: str, instance_id: str):
    region_base_url = config.regions[region]
    machines_api = get_machine_api_client(base_url=region_base_url)

    machines_api.request(
        "DELETE", f"/organizations/{organization_id}/machines/{instance_id}"
    )
