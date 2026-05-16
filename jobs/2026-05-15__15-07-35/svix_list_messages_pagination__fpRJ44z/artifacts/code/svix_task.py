import os
import json
import sys
from svix.api import Svix, ApplicationIn, MessageIn, EventTypeIn, MessageListOptions
from svix.api.errors.http_error import HttpError

def main():
    api_key = os.environ.get("SVIX_API_KEY")
    if not api_key:
        print("SVIX_API_KEY environment variable is not set")
        sys.exit(1)

    svix = Svix(api_key)
    app_uid = "test-app-pagination"
    event_type_name = "user.signup"

    # 1. Create/Get Application
    try:
        svix.application.get(app_uid)
        print(f"Application {app_uid} already exists.")
    except HttpError:
        svix.application.create(ApplicationIn(name="Test App", uid=app_uid))
        print(f"Created application {app_uid}.")
    except Exception as e:
        print(f"Unexpected error getting application: {e}")
        sys.exit(1)

    # 2. Create/Get Event Type
    try:
        svix.event_type.get(event_type_name)
        print(f"Event type {event_type_name} already exists.")
    except HttpError:
        svix.event_type.create(EventTypeIn(name=event_type_name, description="Test"))
        print(f"Created event type {event_type_name}.")
    except Exception as e:
        print(f"Unexpected error getting event type: {e}")
        sys.exit(1)

    # 3. Create 5 messages
    print("Creating 5 messages...")
    for i in range(5):
        msg = svix.message.create(
            app_uid,
            MessageIn(eventType=event_type_name, payload={"test": i})
        )
        print(f"Created message {i+1}/5: {msg.id}")

    import time
    time.sleep(10)

    # 4. Fetch messages with pagination
    print("Fetching messages with limit=2...")
    fetched_ids = []
    iterator = None
    page_count = 0
    
    while True:
        page_count += 1
        response = svix.message.list(app_uid, MessageListOptions(limit=2, iterator=iterator))
        for msg in response.data:
            fetched_ids.append(msg.id)
        
        print(f"Page {page_count}: Fetched {len(response.data)} messages.")
        
        iterator = response.iterator
        if not iterator:
            break

    print(f"Total fetched messages: {len(fetched_ids)}")

    # 5. Write to output.json
    output_path = "/home/user/project/output.json"
    with open(output_path, "w") as f:
        json.dump(fetched_ids, f, indent=2)
    print(f"Saved message IDs to {output_path}")

if __name__ == "__main__":
    main()
