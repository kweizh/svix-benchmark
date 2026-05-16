import os
from datetime import datetime, timedelta, timezone

from svix import Svix
from svix.models import ApplicationIn, EndpointIn, EndpointUpdate, RecoverIn


def main() -> None:
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    if not auth_token:
        raise RuntimeError("SVIX_AUTH_TOKEN environment variable is required")

    svix_client = Svix(auth_token)

    application = svix_client.application.create(ApplicationIn(name="RecoverApp"))
    app_id = application.id

    endpoint = svix_client.endpoint.create(
        app_id,
        EndpointIn(url="http://failing-endpoint.local/webhook", disabled=True),
    )
    endpoint_id = endpoint.id

    svix_client.endpoint.update(
        app_id,
        endpoint_id,
        EndpointUpdate(
            url="http://working-endpoint.local/webhook",
            disabled=False,
        ),
    )

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    svix_client.endpoint.recover(app_id, endpoint_id, RecoverIn(since=since))


if __name__ == "__main__":
    main()
