import azure.functions as func
import logging
from query_llm import query_llm
from azure_speech import azure_speech
import json
from dotenv import load_dotenv
import tempfile
import asyncio
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import uuid
import os

load_dotenv()

url = os.environ.get("COSMOS_ENDPOINT")
key = os.environ.get("COSMOS_KEY")


client = CosmosClient(url, credential=key)
database_name = 'keli'
database = client.get_database_client(database_name)
container_name = 'keli-conversations'
container = database.get_container_client(container_name)
# query = "SELECT * FROM c"
# items = list(container.query_items(query, enable_cross_partition_query=True))
# print(items, flush=True)
#
# new_item = {
#     "id": "70b63682-b93a-4c77-aad2-65501347265f",
#     "categoryId": "61dba35b-4f02-45c5-b648-c6badc0cbd79",
#     "categoryName": "gear-surf-surfboards",
#     "name": "Yamba Surfboard",
#     "quantity": 12,
#     "sale": False,
# }
# container.create_item(new_item)

app = func.FunctionApp()

cors_headers = {
    "Access-Control-Allow-Origin": "*",  # Replace with your allowed origin(s)
    "Access-Control-Allow-Methods": "OPTIONS, POST",  # Add other allowed methods if needed
    "Access-Control-Allow-Headers": "Content-Type",
}

@app.route(route="v1/chat", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def cors_chat_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /v1/chat')
    return func.HttpResponse(headers=cors_headers)

@app.route(route="v1/chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_new_conversation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /v1/chat - Create new chat conversation')

    new_conversation = {
        "id": str(uuid.uuid4()),
        "msgs": [],
    }

    container.create_item(new_conversation)

    return func.HttpResponse(
        status_code=200,
        headers=cors_headers,
        body=json.dumps(new_conversation, separators=(',', ':')),
        mimetype="application/json"
    )

@app.route(route="v1/chat", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def add_message_to_conversation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PUT /v1/chat - User has submitted a new message or question')

    try:
        req_body = req.get_json()
        query = req_body.get("query", "Hello!")
        msgs = req_body.get("msgs", [])
        model = req_body.get("model", "gpt-3.5-turbo")
    except ValueError:
        return func.HttpResponse(
            "Missing request body parameters (query, msgs, or model)",
            status_code=400
        )
        pass

    print(f"query: {query}")
    llm_resp = query_llm(query, msgs, model)

    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    print(temp_file.name)

    speech_resp = asyncio.run(azure_speech(llm_resp['assistant_response']['content'], temp_file.name))

    merged_data = {**llm_resp, **speech_resp}
    merged_json_resp = json.dumps(merged_data, separators=(',', ':'))

    return func.HttpResponse(
        status_code=200,
        headers=cors_headers,
        body=merged_json_resp,
        mimetype="application/json"
    )

# Example merged_json_resp:
# {
#     "assistant_response": {
#         "role": "assistant",
#         "content": "{\"text\": \"Hello world!\", \"facialExpression\": \"smile\", \"animation\": \"Talking_0\"}"
#     },
#     "usage": {
#         "completion_tokens": 24,
#         "prompt_tokens": 241,
#         "total_tokens": 265
#     },
#     "lipsync": {
#         "mouthCues": [
#             {
#                 "start": 0,
#                 "end": 0.05,
#                 "target": "viseme_sil",
#                 "value": 1
#             },
#             ...
#         ]
#     },
#     "audio": "..."
# }

