"""
Budget Storage tool.

Saves the user's confirmed income/expense breakdown to Supabase so it
can be recalled in future conversations. Needs the already-configured
supabase client passed in from main.py (it doesn't create its own
connection, to avoid duplicating credentials).
"""

from datetime import datetime


SAVE_BUDGET_TOOL = {
    "type": "function",
    "function": {
        "name": "save_user_budget",
        "description": (
            "Save the user's income and expense breakdown so it can "
            "be recalled and referenced in future conversations. Use "
            "this once the user has confirmed a budget they want to "
            "keep, not on every message."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "income": {
                    "type": "number",
                    "description": "Monthly income after taxes"
                },
                "expenses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "amount": {"type": "number"}
                        },
                        "required": ["name", "amount"]
                    }
                }
            },
            "required": ["income"]
        }
    }
}


def make_save_user_budget(supabase_client):
    """
    Returns a save_user_budget function bound to the given supabase
    client, so main.py can inject its existing connection.
    """

    def save_user_budget(session_id, user_id, income, expenses=None):

        supabase_client.table("budgets").upsert({
            "session_id": session_id,
            "user_id": user_id,
            "income": income,
            "expenses": expenses or [],
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        return {"status": "saved"}

    return save_user_budget