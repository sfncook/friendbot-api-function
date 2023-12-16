from flask import Flask, request
import os
from salesgpt.agents import SalesGPT
from langchain.chat_models import ChatLiteLLM

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = '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'

llm = ChatLiteLLM(temperature=0.4, model_name="gpt-3.5-turbo")
sales_agent = SalesGPT.from_llm(llm, use_tools=True, verbose=False,
                                product_catalog = "examples/sample_product_catalog.txt",
                                salesperson_name="Ted Lasso",
                                salesperson_role="Sales Representative",
                                company_name="Sleep Haven",
                                company_business='''Sleep Haven 
                            is a premium mattress company that provides
                            customers with the most comfortable and
                            supportive sleeping experience possible. 
                            We offer a range of high-quality mattresses,
                            pillows, and bedding accessories 
                            that are designed to meet the unique 
                            needs of our customers.'''
                                )
sales_agent.seed_agent()
sales_agent.determine_conversation_stage() # optional for demonstration, built into the prompt
# agent
sales_agent.step()
agent_output = sales_agent.conversation_history[-1]
print()
print()
print(agent_output.replace('Ted Lasso:', '').replace('<END_OF_TURN>', ''))
print()
print()

#
# # user
# user_input = input('Your response: ') # Yea, sure
# sales_agent.human_step(user_input)
#
# # agent
# sales_agent.determine_conversation_stage() # optional for demonstration, built into the prompt
# sales_agent.step()
#
# # user
# user_input = input('Your response: ') # What pricing do you have for your mattresses?
# sales_agent.human_step(user_input)
#
# # agent
# sales_agent.determine_conversation_stage() # optional for demonstration, built into the prompt
# sales_agent.step()

@app.route('/hello', methods=['GET'])
def query_hello():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run(debug=True)
