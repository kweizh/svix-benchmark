#!/usr/bin/env python3
import os
import sys

from svix import Svix


def main() -> int:
    auth_token = os.getenv("SVIX_AUTH_TOKEN")
    if not auth_token:
        print("SVIX_AUTH_TOKEN environment variable is required", file=sys.stderr)
        return 1

    svix = Svix(auth_token)

    app = svix.application.create({
        "name": "Custom Header App",
    })

    endpoint = svix.endpoint.create(
        app.id,
        {
            "url": "https://example.com/webhook/",
            "headers": {
                "X-Custom-Auth": "secret-token-123",
            },
        },
    )

    with open("/home/user/project/app_id.txt", "w", encoding="utf-8") as app_file:
        app_file.write(f"{app.id}\n")

    with open("/home/user/project/endpoint_id.txt", "w", encoding="utf-8") as endpoint_file:
        endpoint_file.write(f"{endpoint.id}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
