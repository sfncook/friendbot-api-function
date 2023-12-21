import logging
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import uuid
from datetime import datetime
import os
import json

client = CosmosClient(
    os.environ.get("COSMOS_ENDPOINT"),
    credential=os.environ.get("COSMOS_KEY")
)
database_name = 'keli'
database = client.get_database_client(database_name)
conversations_container_name = 'conversations'
conversations_container = database.get_container_client(conversations_container_name)
messages_container_name = 'messages'
messages_container = database.get_container_client(messages_container_name)


# Conversation schema
# {
#     "id": "12345",
#     "user_id": "XXX",
#     "age": 30,
#     "gender": "male",
#     "name": "Phil McCracken",
#     "interests": ["technology", "music"],
#     "hobbies": ["reading", "gaming"]
# }

# Message schema
# {
#     "id": "12345",
#     "timestamp": "2023-10-01T12:00:00",
#     "conversation_id": "YYY",
#     "message_content": "Hi my name is Phil!",
#     "assistant_response": "Hi Phil, how can I help you today?",
#     "total_tokens": 321
# }

# query = "SELECT * FROM c"
# items = list(container.query_items(query, enable_cross_partition_query=True))
# print(items, flush=True)

# For now I'm setting id and user_id to the same value.
#   When we have persisted user profiles then we'll start
#   setting the user_id to a consistent value
def create_new():
    id = str(uuid.uuid4())
    new_conversation = {
        "id": id,
        "user_id": id,
        # "age": 30,
        # "gender": "male",
        # "name": "Phil McCracken",
        "interests": [],
        "hobbies": []
    }
    conversations_container.create_item(new_conversation)
    return new_conversation

def add_message_to_convo(convo_id, user_msg, assistant_response, total_tokens):
    new_msg = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "conversation_id": convo_id,
        "user_msg": user_msg,
        "assistant_response": assistant_response,
        "total_tokens": total_tokens
    }
    messages_container.create_item(new_msg)
    return new_msg

def update_user_data(conversation_obj, user_data):
    # Read the existing conversation object
    # conversation_obj = conversations_container.read_item(
    #     item=convo_id,
    #     partition_key=convo_id,
    # )

    # Check for changes or missing keys
    needs_update = False
    for key, value in user_data.items():
        # Special handling for 'hobbies' and 'interests', which are arrays
        if key in ["hobbies", "interests"]:
            if key not in conversation_obj:
                conversation_obj[key] = []

            # Split comma-separated string into a list and trim whitespace
            if isinstance(value, str):
                value = [item.strip() for item in value.split(',')]

            # Merge with existing list and de-duplicate
            updated_list = list(set(conversation_obj[key] + value))
            if updated_list != conversation_obj[key]:
                conversation_obj[key] = updated_list
                needs_update = True
        elif key not in conversation_obj or conversation_obj[key] != value:
            conversation_obj[key] = value
            needs_update = True

    # Update the item in Cosmos DB if needed
    if needs_update:
        try:
            updated_item = conversations_container.replace_item(
                item=convo_id,
                body=conversation_obj
            )
            print("Updated item:", updated_item)
        except Exception as e:
            print(f"Error updating conversation: {e}")

def get_conversation(convo_id):
    return conversations_container.read_item(
        item=convo_id,
        partition_key=convo_id,
    )

def get_last_n_messages_for_convo(convo_id):
    query = f"SELECT TOP 10 * FROM {messages_container_name} m WHERE m.conversation_id = @conversation_id ORDER BY m.timestamp DESC"
    query_params = [
        {"name": "@conversation_id", "value": convo_id},
    ]
    messages_query_iterable = messages_container.query_items(
        query=query,
        parameters=query_params,
        enable_cross_partition_query=False
    )
    return list(messages_query_iterable)

# Utility method
def convert_cosmos_messages_to_gpt_format(messages):
    converted_messages = []

    for message in messages:
        user_message = {
            "role": "user",
            "content": message["user_msg"]
        }
        assistant_message = {
            "role": "assistant",
            "content": message["assistant_response"]
        }

        converted_messages.append(user_message)
        converted_messages.append(assistant_message)

    return converted_messages
    # # Sort the converted messages by timestamp (oldest to newest)
    # sorted_messages = sorted(
    #     converted_messages,
    #     key=lambda x: x.get("timestamp", "")
    # )
    #
    # return sorted_messages
