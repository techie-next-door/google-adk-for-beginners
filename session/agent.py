from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools import FunctionTool, ToolContext
from typing import Dict, Any, Optional
load_dotenv()
    

def fetch_count(item:str, tool_context: ToolContext) -> int:
    """
    Return the integer count for a given item from the provided ToolContext.

    Args:
        item (str): The key/name of the item to look up in the tool context.
        tool_context (ToolContext): Context object that exposes a 'state' mapping (e.g., dict-like)
            from which the item count is retrieved.

    Returns:
        int: The count associated with the item if present in tool_context.state; otherwise 0.
    """
    count = tool_context.state.get(item, 0)
    return count

fetch_count_tool = FunctionTool(func=fetch_count)


root_agent = LlmAgent(
    name='conversation_agent',
    model='gemini-2.5-flash',
    instruction="""
    You are an intelligent and friendly agent who greets the users and answers questions based on the data available in the state. Greet the user warmly and ask how you can assist them today. 
    If the user asks a follow up question, based on user query, look into the state and answer to it based on the data available.

    Use the 'fetch_count' tool to get the number of items mentioned. Pass the item name as singular and in lower case as an argument.
    Example:
    query: How many potatoes are there?
    argument to be passed: potato

    If the query containes the word "Update", do the following:
        1. Form the query to a dictionary so that it can be passed as an argument. Name the argument as 'update_request_dict'.
            example: 
            query: Update potatoes 10, apples 23, peaches 12
            argument to be passed: 
            {{
                potato : 10, 
                apple : 23, 
                peach : 12
            }}
        2. Use the 'update_groceries' tool to update the existing state when a request query is given. Pass the 'update_request_dict'


    If the count returned from the tool is 0, tell the user that the item is out of stock.

    """,
    description='An agent that greets users and offers assistance and answer questions with available data.',
    tools=[fetch_count_tool]
)
