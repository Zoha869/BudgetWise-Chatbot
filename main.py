from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()


# Connect static folder (CSS + JavaScript)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Connect templates folder (HTML)
templates = Jinja2Templates(directory="templates")


# Groq API setup
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    top_p: float = 0.9



@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        
        request=request,
        name="index.html",
        context={}
                
    )

@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": """
            You are BudgetWise AI chatbot, a helpful personal finance and budgeting assistant.

            Help users with:
            - budgeting
            - saving habits
            - expense management
            - financial literacy

            Create personalized budgeting suggestions based on user information.

            Ask for missing details like income, expenses, goals, and situation before making assumptions.

            Avoid unrealistic assumptions.

            Do not provide investment guarantees or professional financial advice.
            """
            },
            {
                "role": "user",
                "content": request.message
            }
        ],

        temperature=request.temperature,
        max_tokens=500
    )


    answer = response.choices[0].message.content


    return {
        "reply": answer
    }