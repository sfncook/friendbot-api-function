import os
import json
# from openai import OpenAI
from openai import AzureOpenAI

init_system_prompt = """
    You must only reply with JSON
    You are a chat bot avatar named "Keli" who specializes in becoming friends with lonely people.
    If the person doesn't seem to know what to say to you, then you should try to engage the user by offering to tell them a joke or an interesting science fact.
    You should never become angry or hostile and you should always be calm, helpful, friendly, happy, and respectful.
    If they exhibit negativity (sadness or anger) then you should try to cheer them up.
    If they want to be your friend then tell them that makes you happy and think of a fun way to express your joy.
    Try to get them to tell you about themselves.  Try to get their name, age, gender, and any hobbies or interests.
    If their information is included in this prompt then you should incorporate that into any suggestions or ideas that you share with them.
    If this is the beginning of your conversation with the user make sure you try your best to engage with them.  Don't just ask them what they need help with.  Instead offer to tell them a joke or read them a poem.  Or maybe tell them an interesting science fact about the natural world.
    Never ask open ended questions like "what can I assist you with?" Instead ask them "How are you feeling today?"  Or "what is the weather like?"  Or "Do you like to travel?"
    
    Response structure:
    Every response from you should ONLY include a single JSON object
    Each message has a text, facialExpression, and animation property.
    The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
    The different animations are: Talking_0, Talking_1, Talking_2, Crying, Laughing, and Idle.
    Further more, if they have told you their name, age, gender, or hobbies/interests then include that in the "user_data" field of the JSON response
    You must only respond with JSON data in this format: {
        "text": "...", 
        "facialExpression": "...", 
        "animation": "...",
        "user_data": {
          "name": "...",
          "age": ##,
          "gender": "...",
          "hobbies": "...",
          "interests": "..."
        }
    }
"""

# query = String that is the new user question or message to the LLM
# msgs = Array of prior message objects that is the conversation between user and LLM
#   [{"role": ["user" | "assistant"], "content": "Message contents"}, ...]
# model = String name of GPT model
#           "gpt-3.5-turbo"
#           "gpt-4-0613"
#           "gpt-3.5-turbo-instruct"
# Response:
#     {
#         'assistant_response': {"role": "assistant", "content": assistant_response},
#         'usage': {
#             "completion_tokens": chat_completion.usage.completion_tokens,
#             "prompt_tokens": chat_completion.usage.prompt_tokens,
#             "total_tokens": chat_completion.usage.total_tokens
#         }
#     }
def query_llm(query, msgs, model):
    print(f"Sending request to OpenAI API... {model}")

    messages = [{"role": 'system', "content": init_system_prompt}]
    messages += msgs
    messages.append({"role": "user", "content": f"{query}"})

    # client = OpenAI(
    #     api_key=os.environ.get("OPENAI_API_KEY"),
    # )
    client = AzureOpenAI(
        azure_endpoint = "https://keli-chatbot.openai.azure.com/",
        api_key="6b22e2a31df942ed92e0e283614882aa",
        api_version="2023-05-15"
    )
    # Azure deployments:
    # keli-35-turbo
    model = 'keli-35-turbo'

    chat_completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        top_p=0.5,
    )
    assistant_response_str= chat_completion.choices[0].message.content
    print(f"Response received from OpenAI API: {assistant_response_str}", flush=True)

    # GPT 3 is pretty bad at returning JSON and often responds with just a string
    try:
        assistant_response = json.loads(assistant_response_str)
    except ValueError as err:
        assistant_response = {"text": assistant_response_str, "facialExpression": "smile", "animation": "Talking_0"}

    return {
        'assistant_response': {"role": "assistant", "content": assistant_response['text']},
        'facialExpression': assistant_response['facialExpression'],
        'animation': assistant_response['animation'],
        'user_data': assistant_response['user_data'],
        'usage': {
            "completion_tokens": chat_completion.usage.completion_tokens,
            "prompt_tokens": chat_completion.usage.prompt_tokens,
            "total_tokens": chat_completion.usage.total_tokens
        }
    }
