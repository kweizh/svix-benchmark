import json
import logging
import os
from svix import Svix
from svix.api import ApiException

APP_UID = "test-app-pagination"
EVENT_TYPE = "user.signup"
OUTPUT_PATH = "/home/user/project/output.json"
LOG_PATH = "/home/user/project/output.log"


def setup_logging() -> None:
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def ensure_application(svix: Svix) -> None:
    try:
        svix.application.create({"name": "Test App", "uid": APP_UID})
        logging.info("Created application %s", APP_UID)
    except ApiException as exc:
        if exc.status_code == 409:
            logging.info("Application %s already exists", APP_UID)
            return
        raise


def ensure_event_type(svix: Svix) -> None:
    try:
        svix.event_type.create({"name": EVENT_TYPE, "description": "Test"})
        logging.info("Created event type %s", EVENT_TYPE)
    except ApiException as exc:
        if exc.status_code == 409:
            logging.info("Event type %s already exists", EVENT_TYPE)
            return
        raise


def create_messages(svix: Svix) -> None:
    for i in range(5):
        svix.message.create(
            APP_UID,
            {
                "eventType": EVENT_TYPE,
                "payload": {"test": i},
            },
        )
        logging.info("Created message %s", i)


def list_all_messages(svix: Svix) -> list[str]:
    message_ids: list[str] = []
    iterator = None

    while True:
        response = svix.message.list(APP_UID, limit=2, iterator=iterator)
        message_ids.extend(message.id for message in response.data)
        logging.info("Fetched %s messages", len(response.data))

        if not response.iterator:
            break

        iterator = response.iterator

    return message_ids


def write_output(message_ids: list[str]) -> None:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(message_ids, handle, indent=2)
    logging.info("Wrote %s message IDs to %s", len(message_ids), OUTPUT_PATH)


def main() -> None:
    setup_logging()
    api_key = os.environ["SVIX_API_KEY"]
    svix = Svix(api_key)

    ensure_application(svix)
    ensure_event_type(svix)
    create_messages(svix)
    message_ids = list_all_messages(svix)
    write_output(message_ids)


if __name__ == "__main__":
    main()
