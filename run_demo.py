"""
EcoLoop AI Multi-Agent System - run_demo.py
"""

import json
from graph import build_multiagent_system
from copilot import ask_factory_copilot


def main():
    system = build_multiagent_system()

    forced = {
        9: "energy_spike",
        14: "material_spike",
        18: "maintenance_risk",
    }

    state = {
        "hour": 0,
        "force_anomaly": "",
        "reading": {},
        "history": [],
        "is_end_of_day": False,
        "findings": [],
        "log": [],
    }

    for hour in range(24):
        state["hour"] = hour
        state["force_anomaly"] = forced.get(hour, "")
        state["is_end_of_day"] = (hour == 23)
        state["findings"] = []
        state = system.invoke(state)

    print(f"Ticks run: 24")
    print(f"Total agent invocations logged: {sum(len(e['agents_run']) for e in state['log'])}\n")

    print("=== Multi-agent audit trail ===")
    for entry in state["log"]:
        agents = ", ".join(entry["agents_run"]) if entry["agents_run"] else "Energy Agent, Material Agent"
        marker = "🚩" if entry["flagged"] else "  "
        print(f"{marker} hr{entry['hour']:02d}  agents=[{agents}]")
        for action in entry["actions"]:
            print(f"       -> {action}")

    with open("multiagent_run_log.json", "w") as f:
        json.dump(state["log"], f, indent=2)

    print("\nSaved full log to multiagent_run_log.json")

    print("\n==============================")
    print("FACTORY COPILOT DEMO")
    print("==============================")

    context = json.dumps(state["log"][-3:], indent=2)

    question = (
        "Why did production efficiency decrease today and "
        "what should the factory manager do?"
    )

    answer = ask_factory_copilot(question, context)

    print("\nManager Question:")
    print(question)

    print("\nFactory Copilot:")
    print(answer)


if __name__ == "__main__":
    main()