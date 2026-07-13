from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4
import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from groq import Groq
from dotenv import load_dotenv
from supabase import create_client


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
        "http://localhost:5174",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



session_memory: Dict[str, List[Dict[str, str]]] = {}



client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



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
    user_id=None
):

    supabase.table(
        "sessions"
    ).upsert({

        "id": session_id,

        "user_id": user_id,

        "title": "Chat session",

        "created_at": datetime.utcnow().isoformat()

    }).execute()






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


def create_title(message):
    prompt = f"""
    Create a short 3-5 word title for this chat:
    {message}
    Only return title.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    return response.choices[0].message.content


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


    ensure_session_exists(
        session_id,
        getattr(user, "id", None)
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




    messages = [

        {
            "role": "system",
            "content": """
You are BudgetWise AI chatbot.

Help users with:
- budgeting
- saving
- expense management
- financial literacy

Ask questions before making assumptions.
Do not provide guaranteed investment advice.
"""
        }

    ]



    messages.extend(
        context_messages
    )


    messages.append({

        "role": "user",

        "content": request.message

    })





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