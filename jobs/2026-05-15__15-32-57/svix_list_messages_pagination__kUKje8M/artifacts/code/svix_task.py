import os
import json
from svix import Svix
from svix.api import ApplicationIn, EventTypeIn, MessageIn, MessageListOptions

def main():
    # Initialize Svix client
    svix = Svix(os.environ["SVIX_API_KEY"])
    
    # Log file setup
    log_file = "/home/user/project/output.log"
    
    def log(message):
        print(message)
        with open(log_file, "a") as f:
            f.write(message + "\n")
    
    log("Starting Svix pagination task...")
    
    try:
        # Step 1: Create or get existing application
        app_uid = "test-app-pagination"
        log(f"Creating/getting application with UID: {app_uid}")
        
        app = None
        try:
            # Try to create the application
            app = svix.application.create(ApplicationIn(
                name="Test App",
                uid=app_uid
            ))
            log(f"Created application: {app.id}")
        except Exception as e:
            # If application already exists, just proceed with the UID
            if "already exists" in str(e).lower() or "conflict" in str(e).lower():
                log(f"Application {app_uid} already exists, proceeding with existing application")
                # We'll use the UID directly for message operations
            else:
                log(f"Error creating application: {e}")
                raise
        
        # Step 2: Create event type
        log("Creating event type: user.signup")
        try:
            event_type = svix.event_type.create(EventTypeIn(
                name="user.signup",
                description="Test"
            ))
            log(f"Created event type: {event_type.name}")
        except Exception as e:
            if "already exists" in str(e).lower() or "conflict" in str(e).lower():
                log("Event type user.signup already exists, proceeding...")
            else:
                log(f"Error creating event type: {e}")
                # Event type creation error is not critical, proceed
        
        # Step 3: Send 5 messages
        log("Sending 5 messages...")
        message_ids = []
        for i in range(5):
            try:
                message = svix.message.create(
                    app_uid,
                    MessageIn(
                        event_type="user.signup",
                        payload={"test": i}
                    )
                )
                message_ids.append(message.id)
                log(f"Created message {i+1}/5: {message.id}")
            except Exception as e:
                log(f"Error creating message {i+1}: {e}")
                raise
        
        # Step 4: Fetch all messages with pagination
        log("Fetching messages with pagination (limit=2)...")
        all_message_ids = []
        iterator = None
        page_count = 0
        
        while True:
            page_count += 1
            log(f"Fetching page {page_count}...")
            
            try:
                if iterator:
                    response = svix.message.list(app_uid, MessageListOptions(limit=2, iterator=iterator))
                else:
                    response = svix.message.list(app_uid, MessageListOptions(limit=2))
                
                # Extract message IDs from this page
                for message in response.data:
                    all_message_ids.append(message.id)
                    log(f"  Fetched message: {message.id}")
                
                log(f"  Page {page_count}: Got {len(response.data)} messages, total so far: {len(all_message_ids)}")
                
                # Check if there are more pages
                if response.iterator:
                    iterator = response.iterator
                    log(f"  More pages available, iterator: {iterator}")
                else:
                    log("  No more pages available")
                    break
            except Exception as e:
                log(f"Error fetching page {page_count}: {e}")
                raise
        
        log(f"Total messages fetched: {len(all_message_ids)}")
        log(f"Message IDs: {all_message_ids}")
        
        # Step 5: Save message IDs to output.json
        output_file = "/home/user/project/output.json"
        with open(output_file, "w") as f:
            json.dump(all_message_ids, f, indent=2)
        
        log(f"Saved message IDs to {output_file}")
        log("Task completed successfully!")
        
        return all_message_ids
        
    except Exception as e:
        log(f"Task failed: {e}")
        raise

if __name__ == "__main__":
    main()