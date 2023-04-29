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


class Machine:
    def __init__(self, region: str):
        self.base_url = config.regions[region]
        self.machines_api = get_machine_api_client(base_url=self.base_url)

    def create(
        self,
        app: str,
        name: str = None,
        machine_type: str = "us-central",
        disk_size: int = 10,
        meta: dict = {},
    ):
        self.machines_api.request(
            "POST",
            f"organizations/{organization_id}/machines",
            body={
                "name": name,
                "app": app,
                "machine_type": machine_type,
                "disk_size": disk_size,
                "meta": meta,
            },
        )

    def delete(self, instance_id: str):
        self.machines_api.request(
            "DELETE", f"organizations/{organization_id}/machines/{instance_id}"
        )

    def get_info(self, instance_id: str) -> dict:
        return self.machines_api.request(
            "GET", f"organizations/{organization_id}/machines/{instance_id}"
        )

    def run_command(
        self, instance_id: str, command: str, no_exit_on_error: bool = False
    ) -> dict:
        res = self.machines_api.request(
            "POST",
            f"organizations/{organization_id}/machines/{instance_id}/run_command",
            body={"command": command},
            no_exit_on_error=no_exit_on_error,
        )
        return res
