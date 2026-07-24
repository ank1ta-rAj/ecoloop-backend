from fastapi import FastAPI
from pydantic import BaseModel
import json

from graph import build_multiagent_system
from copilot import ask_factory_copilot

app = FastAPI(title="EcoLoop AI")

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