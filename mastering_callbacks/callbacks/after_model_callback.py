from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.genai import types 
from google.adk.models import LlmResponse
import copy

# --- Define the Callback Function ---
def send_empty_stock_note(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM response after it's received."""
    agent_name = callback_context.agent_name
    print(f"\n=========================== After MODEL Callback ===========================\n")
    print(f"[Callback] After model call for agent: {agent_name}")

    # --- Inspection ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # Assuming simple text response for this example
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
        elif llm_response.content.parts[0].function_call:
             print(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
             return None # Don't modify tool calls in this example
        else:
             print("[Callback] Inspected response: No text content found.")
             return None
    elif llm_response.error_message:
        print(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
        return None
    else:
        print("[Callback] Inspected response: Empty LlmResponse.")
        return None # Nothing to modify

    # --- Modification Example ---
    # Replace "joke" with "funny story" (case-insensitive)
    add_no_stock_note = callback_context.state.get("no_stock_note",False)
    if add_no_stock_note:
        print(f"[Callback] Found 0. Modifying response.")
        # Create a NEW LlmResponse with the modified content
        # Deep copy parts to avoid modifying original if other callbacks exist
        modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
        modified_parts[0].text = original_text + "The Item is out of stock 🙃" # Update the text in the copied part
        new_response = LlmResponse(
             content=types.Content(role="model", parts=modified_parts)
             )
        return new_response # Return the modified response
    else:
        # Return None to use the original llm_response
        return None