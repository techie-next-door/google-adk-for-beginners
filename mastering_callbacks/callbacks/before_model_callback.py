from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional
from google.genai import types 


# --- Define the Callback Function ---
def alter_instructions(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    print(f"\n=========================== Before MODEL Callback ===========================\n")
    print(f"[Callback] Before model call for agent: {agent_name}")

    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")

    # --- Modification Example ---
    # Add a prefix to the system instruction
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    # Ensure system_instruction is Content and parts list exists
    if not isinstance(original_instruction, types.Content):
         # Handle case where it might be a string (though config expects Content)
         original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist

    if last_user_message:
        if "update" in last_user_message.lower():
            print("[Callback] 'update' keyword found. Changing LLM Instruction.")
            update_groceries_instruction = """
                1. Form the query to a dictionary so that it can be passed as an argument. Name the argument as 'update_request_dict'.
                    example: 
                    query: Update potatoes 10, apples 23, peaches 12
                    argument to be passed: 
                    {{
                        potato : 10, 
                        apple : 23, 
                        peach : 12
                    }}
                2. Use the 'update_groceries' tool to update the existing state when a request query is given. Pass the 'update_request_dict'.
                3. Return the tool response as the final response to the user.
                """
            modified_text = (original_instruction.parts[0].text or "") + update_groceries_instruction
            # Modify the instruction
            original_instruction.parts[0].text = modified_text
            llm_request.config.system_instruction = original_instruction
            print(f"[Callback] Modified system instruction \n {modified_text}")

        else:
            print("[Callback] Adding secondary default LLM Instruction.")
            default_instruction = """
                Use the 'fetch_count' tool to get the number of items mentioned. Pass the item name as singular and in lower case as an argument.
                Example:
                query: How many potatoes are there?
                argument to be passed: potato

                Return the tool response as the final response to the user.
                """
            modified_text = (original_instruction.parts[0].text or "") + default_instruction
            # Modify the instruction
            original_instruction.parts[0].text = modified_text
            llm_request.config.system_instruction = original_instruction
            print(f"[Callback] Modified system instruction \n {modified_text}")


    return None