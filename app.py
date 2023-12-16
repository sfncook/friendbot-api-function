from litellm import completion, acompletion
import os
import asyncio
import time

## set ENV variables
os.environ["OPENAI_API_KEY"] = "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"
# os.environ["COHERE_API_KEY"] = "your-cohere-key"

messages = [{ "content": "Hello, how are you?", "role": "user"}]
# model_name="gpt-3.5-turbo-1106"
model_name="gpt-3.5-turbo-instruct"
# "gpt-3.5-turbo"
# "gpt-4-1106-preview"

async def doit():
    print('Start acompletion...')
    response = await acompletion(model=model_name, messages=messages)
    print(response)

# openai call
print('Start completion...')
start_time = time.time()
response = completion(model=model_name, messages=messages)
end_time = time.time()
print(response)
elapsed_time = end_time - start_time
print(f"---> SYNC  Elapsed time: {elapsed_time} seconds")

start_time = time.time()
asyncio.run(doit())
end_time = time.time()
elapsed_time = end_time - start_time
print(f"---> ASYNC Elapsed time: {elapsed_time} seconds")
