#!/usr/bin/env python3
"""
recover.py - Recover a failed webhook endpoint using the Svix SDK.

Steps performed:
  1. Initialize the Svix client from the SVIX_AUTH_TOKEN environment variable.
  2. Create a new application named "RecoverApp".
  3. Create a disabled endpoint (simulating a failed state).
  4. Update the endpoint with a working URL and re-enable it.
  5. Trigger message recovery for the last 24 hours.
"""

import os
from datetime import datetime, timedelta, timezone

from svix.api import (
    ApplicationIn,
    EndpointIn,
    EndpointUpdate,
    RecoverIn,
    Svix,
)


def main() -> None:
    # ------------------------------------------------------------------ #
    # 1. Initialise the Svix client
    # ------------------------------------------------------------------ #
    auth_token = os.environ.get("SVIX_AUTH_TOKEN")
    if not auth_token:
        raise EnvironmentError(
            "SVIX_AUTH_TOKEN environment variable is not set. "
            "Please export it before running this script."
        )

    svix_client = Svix(auth_token)
    print("Svix client initialised.")

    # ------------------------------------------------------------------ #
    # 2. Create the application
    # ------------------------------------------------------------------ #
    app = svix_client.application.create(ApplicationIn(name="RecoverApp"))
    app_id = app.id
    print(f"Application created  → id={app_id!r}  name={app.name!r}")

    # ------------------------------------------------------------------ #
    # 3. Create a disabled endpoint (simulating a failed / broken state)
    # ------------------------------------------------------------------ #
    endpoint = svix_client.endpoint.create(
        app_id,
        EndpointIn(
            url="http://failing-endpoint.local/webhook",
            disabled=True,
        ),
    )
    endpoint_id = endpoint.id
    print(
        f"Endpoint created     → id={endpoint_id!r}  "
        f"url={endpoint.url!r}  disabled={endpoint.disabled}"
    )

    # ------------------------------------------------------------------ #
    # 4. Update the endpoint: fix the URL and re-enable it
    # ------------------------------------------------------------------ #
    updated = svix_client.endpoint.update(
        app_id,
        endpoint_id,
        EndpointUpdate(
            url="http://working-endpoint.local/webhook",
            disabled=False,
        ),
    )
    print(
        f"Endpoint updated     → id={updated.id!r}  "
        f"url={updated.url!r}  disabled={updated.disabled}"
    )

    # ------------------------------------------------------------------ #
    # 5. Recover failed messages for the last 24 hours
    # ------------------------------------------------------------------ #
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    svix_client.endpoint.recover(
        app_id,
        endpoint_id,
        RecoverIn(since=since),
    )
    print(f"Recovery triggered   → replaying messages since {since.isoformat()}")

    print("\nDone. Endpoint recovery workflow completed successfully.")


if __name__ == "__main__":
    main()
