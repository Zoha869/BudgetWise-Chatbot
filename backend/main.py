from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4
import json
import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from groq import Groq
from dotenv import load_dotenv
from supabase import create_client

from tools.market_data import MARKET_DATA_TOOL, get_market_data
from tools.news import NEWS_TOOL, get_financial_news
from tools.Calculator import (
    CALCULATOR_TOOLS,
    calculate_budget,
    calculate_loan_emi
)
from tools.save_user_budget import SAVE_BUDGET_TOOL, make_save_user_budget
from security import (
    detect_injection_attempt,
    wrap_user_content,
    BASE_SYSTEM_PROMPT,
    REMINDER_MESSAGE
)


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Supabase configuration missing"
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://budget-wise-chatbot-6fdy.vercel.app/",
        "https://budget-wise-chatbot-6fdy.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],
)


session_memory: Dict[str, List[Dict[str, str]]] = {}


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------------------------------------------
# Tools (5 total): 2 mandatory (API keys already in .env), 3 chosen
# ---------------------------------------------------------------------

save_user_budget = make_save_user_budget(supabase)

TOOLS = [
    MARKET_DATA_TOOL,        # mandatory - ALPHA_VANTAGE_KEY in .env
    NEWS_TOOL,                # mandatory - NEWS_API_KEY in .env
    SAVE_BUDGET_TOOL,
    *CALCULATOR_TOOLS,        # calculate_budget, calculate_loan_emi
]

TOOL_IMPLEMENTATIONS = {
    "get_market_data": get_market_data,
    "get_financial_news": get_financial_news,
    "save_user_budget": save_user_budget,
    "calculate_budget": calculate_budget,
    "calculate_loan_emi": calculate_loan_emi,
}


class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    top_p: float = 0.9
    session_id: Optional[str] = None


def get_user_from_auth(
    authorization: Optional[str]
):

    if not authorization:
        return None

    if not authorization.lower().startswith("bearer "):
        return None

    token = authorization[7:]

    if not token:
        return None

    result = supabase.auth.get_user(token)

    user = getattr(
        result,
        "user",
        None
    )

    return user


def assert_session_access(
    session_id: str,
    user_id: str
):

    result = (
        supabase
        .table("sessions")
        .select("user_id")
        .eq("id", session_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if result.data["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


def ensure_user_profile(user):

    if not user:
        return

    profile = {

        "id": user.id,

        "email": getattr(
            user,
            "email",
            None
        ),

        "full_name": (
            user.user_metadata.get("full_name")
            if getattr(user, "user_metadata", None)
            else None
        ),

        "created_at": datetime.utcnow().isoformat()

    }

    supabase.table(
        "users"
    ).upsert(profile).execute()


def ensure_session_exists(
    session_id,
    user_id=None,
    title=None
):

    payload = {
        "id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }

    if title is not None:
        payload["title"] = title

    supabase.table(
        "sessions"
    ).upsert(payload).execute()


def load_session_context(session_id):

    if session_id in session_memory:
        return session_memory[session_id]

    result = (
        supabase
        .table("messages")
        .select("role,content")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    messages = []

    if result.data:

        messages = [

            {
                "role": row["role"],
                "content": row["content"]
            }

            for row in result.data

        ]

    session_memory[session_id] = messages

    return messages


def append_session_message(
    session_id,
    role,
    content,
    user_id=None
):

    session_memory.setdefault(
        session_id,
        []
    ).append({

        "role": role,

        "content": content

    })

    supabase.table(
        "messages"
    ).insert({

        "id": str(uuid4()),

        "session_id": session_id,

        "user_id": user_id,

        "role": role,

        "content": content,

        "created_at": datetime.utcnow().isoformat()

    }).execute()


@app.get("/")
def home():

    return {
        "message": "BudgetWise API is running"
    }


def generate_chat_title(message):
    prompt = f"""
Generate a very short title (maximum 4 words).

Examples:
How should I pay off debt?
Title:
Debt Payoff Plan

I need a monthly budget
Title:
Monthly Budget

User message:
{message}

Only output the title.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )

        title = response.choices[0].message.content.strip().replace('"', "")

        print("Generated Title:", title)

        return title

    except Exception as e:
        print("TITLE ERROR:", e)
        return "Chat session"


@app.get("/sessions")
def get_sessions(
    authorization: Optional[str] = Header(None)
):

    user = get_user_from_auth(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    result = (
        supabase
        .table("sessions")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data


@app.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: str,
    authorization: Optional[str] = Header(None)
):

    user = get_user_from_auth(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    assert_session_access(session_id, user.id)

    result = (
        supabase
        .table("messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    return result.data


@app.post("/chat")
def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None)
):

    user = get_user_from_auth(
        authorization
    )

    if user:
        ensure_user_profile(user)

    session_id = (
        request.session_id
        or str(uuid4())
    )

    existing = (
        supabase
        .table("sessions")
        .select("id, title, user_id")
        .eq("id", session_id)
        .execute()
    )

    is_new_session = len(existing.data) == 0

    # Security: if this session already belongs to someone, make sure
    # the caller is actually that owner before letting them post to it
    # or read its history. Prevents one user from hijacking another
    # user's session by sending/guessing its session_id.
    if not is_new_session:

        owner_id = existing.data[0].get("user_id")
        caller_id = getattr(user, "id", None)

        if owner_id is not None and owner_id != caller_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this session"
            )

    current_title = (
        existing.data[0].get("title")
        if existing.data
        else None
    )

    placeholder_titles = {
        None,
        "",
        "Chat session",
        "New Chat"
    }

    needs_title = is_new_session or (current_title in placeholder_titles)

    session_title = (
        generate_chat_title(request.message)
        if needs_title
        else None
    )

    print("Is New Session:", is_new_session)
    print("Session Title:", session_title)

    ensure_session_exists(
        session_id,
        getattr(user, "id", None),
        title=session_title
    )

    context_messages = load_session_context(
        session_id
    )

    append_session_message(
        session_id,
        "user",
        request.message,
        getattr(user, "id", None)
    )

    injection_detected = detect_injection_attempt(request.message)

    if injection_detected:
        print("SECURITY WARNING: possible prompt injection attempt:", request.message)

    messages = [

        {
            "role": "system",
            "content": BASE_SYSTEM_PROMPT
        }

    ]

    messages.extend(
        context_messages
    )

    messages.append({

        "role": "user",

        "content": wrap_user_content(request.message)

    })

    if injection_detected:
        messages.append(REMINDER_MESSAGE)

    # ---------------------------------------------------------------
    # Step 1: non-streaming call to check if the model wants a tool
    # ---------------------------------------------------------------

    tool_check = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=messages,

        temperature=request.temperature,

        top_p=request.top_p,

        max_tokens=500,

        tools=TOOLS,

        tool_choice="auto"

    )

    tool_message = tool_check.choices[0].message
    tool_calls = getattr(tool_message, "tool_calls", None)

    if tool_calls:

        messages.append({
            "role": "assistant",
            "content": tool_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        })

        for tc in tool_calls:

            fn_name = tc.function.name
            fn = TOOL_IMPLEMENTATIONS.get(fn_name)

            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            if fn_name == "save_user_budget":
                args["session_id"] = session_id
                args["user_id"] = getattr(user, "id", None)

            try:
                result = fn(**args) if fn else {"error": "unknown tool"}
            except Exception as e:
                result = {"error": str(e)}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": fn_name,
                "content": json.dumps(result)
            })

    # ---------------------------------------------------------------
    # Step 2: stream the final natural-language reply
    # ---------------------------------------------------------------

    stream_response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=messages,

        temperature=request.temperature,

        top_p=request.top_p,

        max_tokens=500,

        stream=True

    )

    def event_generator():

        assistant_text = ""

        for chunk in stream_response:

            for choice in chunk.choices:

                content = choice.delta.content

                if content:

                    assistant_text += content

                    yield content

        if assistant_text:

            append_session_message(

                session_id,

                "assistant",

                assistant_text

            )

    headers = {

        "X-Session-Id": session_id

    }

    return StreamingResponse(

        event_generator(),

        media_type="text/plain",

        headers=headers

    )