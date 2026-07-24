"""
EcoLoop AI Multi-Agent System - graph.py

Real multi-agent LangGraph matching the canvas: a Supervisor Agent
inspects each reading and DYNAMICALLY DISPATCHES to whichever
specialist agents are relevant this tick (via LangGraph's Send API --
genuine parallel fan-out, not a fixed linear chain). Their findings
converge on a Report Generator / Action Recommender node, matching
the architecture diagram (Supervisor -> {Energy, Material,
Maintenance, ESG} -> Report Generator).

Routing logic (the Supervisor's actual "reasoning"):
  - Energy Agent   -> runs every tick (core monitoring)
  - Material Agent -> runs every tick (core monitoring)
  - Maintenance Agent -> runs only when vibration/temp looks risky
  - ESG Agent      -> runs only at end-of-day (compliance rollup)

n8n's role in production: the Report Generator's output is what an
n8n workflow would pick up to fan out notifications (Slack/email/
WhatsApp) and write to a dashboard DB -- not re-implemented here,
since that's an integration/automation layer, not agent reasoning.
"""

from __future__ import annotations
import operator
from typing import TypedDict, List, Annotated
import numpy as np

from langgraph.graph import StateGraph, END
from langgraph.types import Send

from sensors import sense_reading
from agents import energy_agent, material_agent, maintenance_agent, esg_agent
from supervisor import supervisor_reason

from approval import manager_approval

_RNG = np.random.default_rng(11)


class AgentState(TypedDict):
    hour: int
    force_anomaly: str
    reading: dict
    history: List[dict]
    is_end_of_day: bool
    findings: Annotated[List[dict], operator.add]
    log: Annotated[List[dict], operator.add]


def sense_node(state: AgentState) -> AgentState:
    # NOTE: findings is reset by the driver script before each invoke()
    # call, not here -- operator.add reducers MERGE node outputs, they
    # can't be used to clear a list mid-graph (returning [] just adds
    # [] to whatever's already there).
    reading = sense_reading(_RNG, state["hour"], state.get("force_anomaly") or None)
    return {"reading": reading}


def supervisor_route(state: AgentState) -> List[Send]:

    reading = state["reading"]
    history = state["history"]

    decision = supervisor_reason(reading, history)

    dispatch = [
        Send("energy_agent", {"reading": reading, "history": history}),
        Send("material_agent", {"reading": reading, "history": history}),
    ]

    if decision in ["warning", "critical"]:
        dispatch.append(
            Send(
                "maintenance_agent",
                {
                    "reading": reading,
                    "history": history,
                },
            )
        )

    if state.get("is_end_of_day") or decision == "critical":
        dispatch.append(
            Send(
                "esg_agent",
                {
                    "reading": reading,
                    "history": history,
                },
            )
        )

    return dispatch


def energy_agent_node(state: dict) -> AgentState:
    finding = energy_agent(state["reading"], state["history"])
    return {"findings": [finding]} if finding else {"findings": []}


def material_agent_node(state: dict) -> AgentState:
    finding = material_agent(state["reading"], state["history"])
    return {"findings": [finding]} if finding else {"findings": []}


def maintenance_agent_node(state: dict) -> AgentState:

    previous_findings = []

    for f in state.get("findings", []):
        if f.get("is_anomaly"):
            previous_findings.append(
                f"{f['agent']}: {f['finding']}"
            )

    finding = maintenance_agent(
        state["reading"],
        state["history"],
        previous_findings
    )

    return {"findings": [finding]} if finding else {"findings": []}


def esg_agent_node(state: dict) -> AgentState:
    finding = esg_agent(state["reading"], state["history"])
    return {"findings": [finding]} if finding else {"findings": []}


def report_node(state: AgentState) -> AgentState:

    findings = state["findings"]

    actions = []
    approvals = []

    for f in findings:

        if f.get("action"):

            actions.append(f["action"])

            confidence = f.get("confidence", 0)

            approval = manager_approval(confidence)

            approvals.append({
                "agent": f["agent"],
                "confidence": confidence,
                "status": approval
            })

    entry = {
        "hour": state["reading"]["hour"],
        "reading": state["reading"],
        "agents_run": [f["agent"] for f in findings],
        "flagged": any(f["is_anomaly"] for f in findings),
        "findings": findings,
        "actions": actions if actions else ["All systems operating normally."],
        "approvals": approvals
    }

    new_history = state["history"] + [state["reading"]]

    return {
        "history": new_history,
        "log": [entry]
    }


def build_multiagent_system():
    graph = StateGraph(AgentState)
    graph.add_node("sense", sense_node)
    graph.add_node("energy_agent", energy_agent_node)
    graph.add_node("material_agent", material_agent_node)
    graph.add_node("maintenance_agent", maintenance_agent_node)
    graph.add_node("esg_agent", esg_agent_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("sense")
    # Supervisor's dispatch logic lives in the conditional edge itself
    graph.add_conditional_edges("sense", supervisor_route)

    for agent_node in ["energy_agent", "material_agent", "maintenance_agent", "esg_agent"]:
        graph.add_edge(agent_node, "report")

    graph.add_edge("report", END)

    return graph.compile()
