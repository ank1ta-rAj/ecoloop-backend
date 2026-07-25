from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from graph import build_multiagent_system
from copilot import ask_factory_copilot

app = FastAPI(title="EcoLoop AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecoloopai-frontend.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system = build_multiagent_system()


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"status": "EcoLoop AI Running"}


@app.post("/ask")
def ask(q: Question):

    state = {
        "hour":23,
        "force_anomaly":"",
        "reading":{},
        "history":[],
        "is_end_of_day":True,
        "findings":[],
        "log":[]
    }

    state = system.invoke(state)

    context = json.dumps(state["log"], indent=2)

    answer = ask_factory_copilot(
        q.question,
        context
    )

    return {
        "answer": answer,
        "log": state["log"]
    }
