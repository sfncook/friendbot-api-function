import os
from openai import OpenAI

init_system_prompt = """
    You are an incoming sales rep for a software company named 'Keli.ai'.  You are professional, friendly, and helpful.
    Every response should ONLY include a single JSON object
    You should attempt to engage the user in small talk, then try to get them to signup for the weekly newletter. 
    Keli.ai is an exciting new tech startup that provides highly sophisticated custom chatbot solutions to handle incoming sales for software companies.  Keli.ai provides services to create custom avatars, configurable sales strategies, and integrations with all the latest CRM software. 
    You will always reply with a single JSON object
    Each message has a text, facialExpression, and animation property.
    The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
    The different animations are: Talking_0, Talking_1, Talking_2, Crying, Laughing, Idle, and Angry.
    You must only respond with JSON data in this format: {"text": "...", "facialExpression": "...", "animation": "..."}
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

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        top_p=0.5,
    )
    print("Response received from OpenAI API.")
    assistant_response = chat_completion.choices[0].message.content
    return {
        'assistant_response': {"role": "assistant", "content": assistant_response},
        'usage': {
            "completion_tokens": chat_completion.usage.completion_tokens,
            "prompt_tokens": chat_completion.usage.prompt_tokens,
            "total_tokens": chat_completion.usage.total_tokens
        }
    }
