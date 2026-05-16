#!/usr/bin/env python3
"""
Svix List Messages Pagination Script

Creates a test application, sends 5 messages, then fetches all messages
using paginated list calls (limit=2) and writes the IDs to output.json.
"""

import json
import logging
import os
import sys

from svix import Svix
from svix.api import ApplicationIn, EventTypeIn, MessageIn, MessageListOptions

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOG_FILE = "/home/user/project/output.log"
OUTPUT_FILE = "/home/user/project/output.json"
APP_UID = "test-app-pagination"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Initialise Svix client
    # ------------------------------------------------------------------
    api_key = os.environ.get("SVIX_API_KEY")
    if not api_key:
        log.error("SVIX_API_KEY environment variable is not set.")
        sys.exit(1)

    svix = Svix(api_key)
    log.info("Svix client initialised.")

    # ------------------------------------------------------------------
    # 2. Create (or re-use) the application
    # ------------------------------------------------------------------
    log.info("Creating application with UID '%s'...", APP_UID)
    try:
        app = svix.application.create(
            ApplicationIn(name="Test App", uid=APP_UID)
        )
        log.info("Application created: id=%s uid=%s", app.id, app.uid)
    except Exception as exc:
        # If the application already exists Svix returns a 409 / error.
        # Try to get it by UID instead.
        log.warning("Could not create application (%s). Attempting to fetch existing one.", exc)
        try:
            # get_or_create semantics: use get with the UID as the app_id
            app = svix.application.get(APP_UID)
            log.info("Fetched existing application: id=%s uid=%s", app.id, app.uid)
        except Exception as exc2:
            log.error("Failed to get existing application: %s", exc2)
            sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Create event type (ignore if it already exists)
    # ------------------------------------------------------------------
    log.info("Creating event type 'user.signup'...")
    try:
        et = svix.event_type.create(
            EventTypeIn(name="user.signup", description="Test event type")
        )
        log.info("Event type created: %s", et.name)
    except Exception as exc:
        log.info("Event type may already exist (ignored): %s", exc)

    # ------------------------------------------------------------------
    # 4. Send 5 messages
    # ------------------------------------------------------------------
    sent_ids: list[str] = []
    for i in range(1, 6):
        log.info("Sending message %d/5...", i)
        try:
            msg = svix.message.create(
                APP_UID,
                MessageIn(
                    event_type="user.signup",
                    payload={"test": i},
                ),
            )
            sent_ids.append(msg.id)
            log.info("  Message sent: id=%s", msg.id)
        except Exception as exc:
            log.error("Failed to send message %d: %s", i, exc)
            sys.exit(1)

    log.info("All 5 messages sent: %s", sent_ids)

    # ------------------------------------------------------------------
    # 5. Fetch all messages using paginated list (limit=2)
    # ------------------------------------------------------------------
    log.info("Fetching messages with limit=2 (paginated)...")
    all_ids: list[str] = []
    iterator: str | None = None
    page = 0

    while True:
        page += 1
        options = MessageListOptions(limit=2, iterator=iterator)
        response = svix.message.list(APP_UID, options)

        page_ids = [m.id for m in response.data]
        log.info(
            "  Page %d: fetched %d message(s) %s  done=%s  iterator=%s",
            page,
            len(page_ids),
            page_ids,
            response.done,
            response.iterator,
        )
        all_ids.extend(page_ids)

        if response.done:
            log.info("Pagination complete (done=True).")
            break

        if not response.iterator:
            log.info("Pagination complete (no next iterator).")
            break

        iterator = response.iterator

    log.info("Total messages fetched: %d  IDs: %s", len(all_ids), all_ids)

    # ------------------------------------------------------------------
    # 6. Write IDs to output.json
    # ------------------------------------------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(all_ids, fh, indent=2)
    log.info("Message IDs written to %s", OUTPUT_FILE)


if __name__ == "__main__":
    main()
