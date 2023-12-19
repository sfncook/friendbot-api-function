import azure.functions as func
import logging
from query_llm import query_llm
from azure_speech import azure_speech
import json
from dotenv import load_dotenv
import tempfile
import asyncio

load_dotenv()

app = func.FunctionApp()

@app.route(route="v1/chat", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def cors_chat_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /v1/chat')

    # Define CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",  # Replace with your allowed origin(s)
        "Access-Control-Allow-Methods": "OPTIONS, POST",  # Add other allowed methods if needed
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return func.HttpResponse(headers=headers)

@app.route(route="v1/chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /v1/chat')

    try:
        req_body = req.get_json()
        query = req_body.get("query")
        msgs = req_body.get("msgs")
        model = req_body.get("model")
    except ValueError:
        return func.HttpResponse(
            "Missing request body parameters (query, msgs, or model)",
            status_code=400
        )
        pass

    llm_resp = query_llm(query, msgs, model)

    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    print(temp_file.name)

    speech_resp = asyncio.run(azure_speech(llm_resp['assistant_response']['content'], temp_file.name))

    merged_data = {**llm_resp, **speech_resp}
    merged_json_resp = json.dumps(merged_data)

    return func.HttpResponse(merged_json_resp)

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

