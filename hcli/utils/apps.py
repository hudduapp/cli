import sys

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "http://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {token}"},
)


def get_app(app: str) -> dict:
    try:
        return core_api.request(
            "POST", f"/organizations/{organization_id}/apps/search?limit=1&name={app}"
        )["data"][0]
    except:
        print(
            f"[red]Couldn't find app with name [bold]{app}[/bold]. Make sure it exists by checking with [bold]hcli apps list[/bold][/red]"
        )
        sys.exit()
