# Svix List Messages Pagination

## Background
Svix is an enterprise-grade webhooks-as-a-service platform. When retrieving messages for an application, the results are paginated. You need to write a Python script that sets up a test application, sends several messages, and then fetches all of them using pagination.

## Requirements
- Write a Python script `/home/user/project/svix_task.py`.
- The script must initialize the `Svix` client using the `SVIX_API_KEY` environment variable.
- The script must create a new application with the UID `test-app-pagination`. If an application with this UID already exists, the script must gracefully handle it (e.g., by deleting and recreating it, or just proceeding to use it).
- The script must create 5 messages for this application. You can use any valid payload and a dummy event type like `user.signup` (you may need to create the event type first if Svix requires it, or just send the message if event types are auto-created/optional depending on your environment. Actually, Svix requires event types to be created, so create an event type `user.signup` first).
- After creating the 5 messages, the script must fetch all messages for the application `test-app-pagination`.
- You MUST use `limit=2` in the `svix.message.list` API call to force pagination.
- Iterate through the pages using the `iterator` returned in each response until all messages are fetched.
- Extract the `id` of each fetched message and save the complete list of message IDs as a JSON array to `/home/user/project/output.json`.

## Implementation Guide
1. Initialize `Svix(os.environ["SVIX_API_KEY"])`.
2. Create application: `svix.application.create({"name": "Test App", "uid": "test-app-pagination"})`.
3. Create event type: `svix.event_type.create({"name": "user.signup", "description": "Test"})` (ignore if it already exists).
4. Send 5 messages using `svix.message.create("test-app-pagination", {"eventType": "user.signup", "payload": {"test": i}})`.
5. Call `svix.message.list("test-app-pagination", limit=2)`.
6. Keep track of the message IDs.
7. If the response has an `iterator`, pass it to the next `list` call as `iterator=response.iterator`.
8. Write the list of IDs to `/home/user/project/output.json`.

## Constraints
- Project path: `/home/user/project`
- Output file: `/home/user/project/output.json`
- Log file: `/home/user/project/output.log`
- The `SVIX_API_KEY` environment variable is available in the environment.