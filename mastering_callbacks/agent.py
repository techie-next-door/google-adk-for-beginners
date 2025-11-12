from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools import FunctionTool, ToolContext
from typing import Dict, Any, Optional

from callbacks import (check_if_agent_should_run, alter_instructions, validate_tool_args,
                       send_discount_coupon, send_empty_stock_note, validate_tool_response)
load_dotenv()


def update_groceries(update_request_dict:Dict[str, Any], tool_context: ToolContext) -> Dict[str,Any]:
    """
    Update the 'groceries' entry in the provided ToolContext.state with the given mapping and return a result summary.

    Args:
        update_request_dict (Dict[str, Any]): Mapping containing groceries data to store under the 'groceries' key.
        tool_context (ToolContext): Context object exposing a mutable 'state' mapping (e.g., dict-like). The function calls tool_context.state.update({'groceries': update_request_dict}).

    Returns:
        Dict[str, str]: A dictionary summarizing the operation with two keys:
            - "status": "success" if the update completed without exception, otherwise "failure".
            - "message": A human-readable message describing the outcome; on failure this includes the exception text.
    """
    message = None
    status = None
    try:
        tool_context.state.update({'groceries': update_request_dict})
        message = "✅ Groceries Updated Successfully!"
        status = "success"
    except Exception as e:
        status = "failure"
        message = f"❌ There is an error, {e}"

    return {"status": status, "message": message}
    

def fetch_count(item:str, tool_context: ToolContext) -> Dict[str,int]:
    """
    Return the integer count for a given item from the provided ToolContext.

    Args:
        item (str): The key/name of the item to look up in the tool context.
        tool_context (ToolContext): Context object that exposes a 'state' mapping (e.g., dict-like)
            from which the item count is retrieved.

    Returns:
        Dict[str,int]: The count associated with the item if present in tool_context.state; otherwise 0.
    """
    count: int = tool_context.state.get(item, 0)
    return {"result": count}

fetch_count_tool = FunctionTool(func=fetch_count)
update_groceries_tool = FunctionTool(func=update_groceries)


root_agent = LlmAgent(
    name='conversation_agent',
    model='gemini-2.5-flash',
    instruction="""
    You are an intelligent and friendly agent who answers questions based on the data available in the state.
    If the user asks a follow up question, based on user query, look into the state and answer to it based on the data available.

    Follow the given instructions below and return the final response to the user.

    """,
    description='An agent that greets users and offers assistance and answer questions with available data.',
    tools=[fetch_count_tool, update_groceries_tool],
    before_agent_callback= check_if_agent_should_run, #Check if the agent got a query other than hi, hello
    before_model_callback= alter_instructions, #Modify the instruction based on the user query
    before_tool_callback= validate_tool_args, #Check if tool args are passed correctly
    after_tool_callback= validate_tool_response, #Check tool response
    after_model_callback= send_empty_stock_note, #Check if the asked stock is empty
    after_agent_callback= send_discount_coupon #Send a discount coupon if user is lucky
)
