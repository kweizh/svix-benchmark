import os
import json
from svix.api import Svix
from svix.models import ApplicationIn, EventTypeIn, MessageIn
from svix.api.message import MessageListOptions

def main():
    svix_client = Svix(os.environ["SVIX_API_KEY"])

    # 1. Create or get application
    app_uid = "test-app-pagination"
    svix_client.application.get_or_create(ApplicationIn(name="Test App", uid=app_uid))

    # 2. Create event type (ignore if exists)
    try:
        svix_client.event_type.create(EventTypeIn(name="user.signup", description="Test Event"))
    except Exception:
        pass

    # 3. Create 5 messages
    for i in range(5):
        svix_client.message.create(
            app_uid,
            MessageIn(event_type="user.signup", payload={"test": i})
        )

    # 4. Fetch all messages with pagination
    all_ids = []
    iterator = None

    while True:
        options = MessageListOptions(limit=2, iterator=iterator)
        response = svix_client.message.list(app_uid, options=options)
        
        for msg in response.data:
            all_ids.append(msg.id)
            
        if response.iterator:
            iterator = response.iterator
        else:
            break

    # 5. Save to output.json
    output_path = "/home/user/project/output.json"
    with open(output_path, "w") as f:
        json.dump(all_ids, f, indent=2)

    print(f"Successfully saved {len(all_ids)} message IDs to {output_path}")

if __name__ == "__main__":
    main()
