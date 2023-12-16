import azure.functions as func
import logging
from query_llm import query_llm
import json

app = func.FunctionApp()

@app.route(route="", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse("Hello world!")

@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST /chat')

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

    resp = query_llm(query, msgs, model)
    return func.HttpResponse(json.dumps(resp))

