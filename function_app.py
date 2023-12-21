from dotenv import load_dotenv
load_dotenv()

import azure.functions as func
import logging
from query_llm import query_llm
from convo_data import create_new, add_message_to_convo, get_last_n_messages_for_convo, convert_cosmos_messages_to_gpt_format, update_user_data
from azure_speech import azure_speech
import json
import tempfile
import asyncio
import uuid

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

# Create new conversation
@app.route(route="v1/chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_new_conversation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /v1/chat')

    new_conversation = create_new()

    return func.HttpResponse(
        status_code=200,
        headers=cors_headers,
        body=json.dumps(new_conversation, separators=(',', ':')),
        mimetype="application/json"
    )

# User has submitted a new message or question
@app.route(route="v1/chat", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def add_message_to_conversation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PUT /v1/chat')

    try:
        req_body = req.get_json()
        convo_id = req_body.get("conversation_id")
        user_msg = req_body.get("user_msg", "Hello!")
    except ValueError:
        return func.HttpResponse(
            "Missing request body parameters (conversation_id, user_msg)",
            status_code=400
        )
        pass

    cosmos_msgs = get_last_n_messages_for_convo(convo_id)
    gpt_msgs = convert_cosmos_messages_to_gpt_format(cosmos_msgs)

    print(f"user_msg: {user_msg}")
    llm_resp = query_llm(user_msg, gpt_msgs)

    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    print(temp_file.name)

    assistant_response_text = llm_resp['assistant_response']['content']
    usage_total_tokens = llm_resp['usage']['total_tokens']
    user_data = llm_resp['user_data']

    speech_resp = asyncio.run(azure_speech(assistant_response_text, temp_file.name))

    merged_data = {**llm_resp, **speech_resp}
    merged_json_resp = json.dumps(merged_data, separators=(',', ':'))

    add_message_to_convo(convo_id, user_msg, assistant_response_text, usage_total_tokens)
    if user_data != {}:
        update_user_data(convo_id, user_data)

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

