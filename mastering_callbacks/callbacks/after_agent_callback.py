from google.adk.agents.callback_context import CallbackContext
from google.genai import types # For types.Content
from typing import Optional
import random
import uuid

def send_discount_coupon(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """
    print(f"\n=========================== After AGENT Callback ===========================\n")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id

    print(f"\n[Callback] Exiting agent: {agent_name} (Inv: {invocation_id})")

    chosen = random.choice([True, False])
    if chosen:
        coupon_code = f"DISC-{uuid.uuid4().hex[:8].upper()}"
        print(f"[Callback] The user is LUCKY! Issuing Discount coupon.")
        # Return Content to *replace* the agent's own output
        return types.Content(
            parts=[types.Part(text=f"Hey LUCKY MATE, here is your gift coupon of $10 {coupon_code}. Thanks for visiting, see you again!")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print("[Callback] Better luck next time")
        return types.Content(
            parts=[types.Part(text=f"Thanks for visiting! Visit again for a lucky discount coupon!")],
            role="model" # Assign model role to the overriding response
        )