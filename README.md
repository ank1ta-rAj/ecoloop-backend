# EcoLoop AI — Multi-Agent System (LangGraph)

This is the architecture that matches the canvas: a **Supervisor**
that dynamically dispatches to specialist agents, not a single linear
pipeline. Verified running end-to-end in this environment — see
`multiagent_run_log.json` for the actual output of a 24-hour simulated
run.

## Architecture

```
                    ┌─────────────┐
                    │    sense    │  (IoT reading: energy, material,
                    └──────┬──────┘   vibration, temp)
                           │
                    ┌──────▼──────┐
                    │ Supervisor  │  dispatch logic = the conditional
                    │  (routing)  │  edge in graph.py: supervisor_route()
                    └──┬───┬───┬──┘
              always   │   │   │ conditional
        ┌──────────────┘   │   └────────────────┐
        ▼                  ▼                     ▼ (only if risky)
  ┌───────────┐     ┌─────────────┐      ┌─────────────────┐
  │  Energy   │     │  Material   │      │   Maintenance    │
  │  Agent    │     │  Agent      │      │   Agent          │
  └─────┬─────┘     └──────┬──────┘      └────────┬─────────┘
        │                  │                       │
        └──────────────────┴───────────┬───────────┘
                                        │      ┌─────────────┐
                                        │      │  ESG Agent  │ (end of day only)
                                        │      └──────┬──────┘
                                        ▼             │
                              ┌──────────────────┐    │
                              │  Report Generator │◄───┘
                              │ / Action Recommender│
                              └──────────────────┘
```

This uses LangGraph's `Send` API for genuine dynamic fan-out — the
Supervisor decides, per tick, exactly which agents to invoke, rather
than always running a fixed set.

## Files

- `sensors.py` — simulated IoT feed (energy, material, vibration, temp)
- `agents.py` — the 4 specialist agents, each independent, single
  responsibility. `action` fields are where a real LLM (IBM Granite via
  watsonx, called only on findings) plugs in — templated here so the
  whole system runs offline.
- `graph.py` — the actual LangGraph: Supervisor dispatch logic
  (`supervisor_route`), specialist agent nodes, Report Generator node
- `run_demo.py` — drives the system across a simulated day, prints the
  full multi-agent audit trail, saves `multiagent_run_log.json`

## Run it

```bash
pip install langgraph langchain-core numpy
cd ecoloop_multiagent
python3 run_demo.py
```

## A bug worth knowing about (already fixed, but instructive)

The first version of this had `findings` accumulating forever across
ticks — a LangGraph gotcha: fields using an `operator.add` reducer
(needed so parallel agents can each contribute a finding without
overwriting each other) **can't be reset by a node returning an empty
list** — that just adds `[]` to what's already there. The fix: the
driver script (`run_demo.py`) explicitly resets `state["findings"] = []`
before each `invoke()` call, since that's outside the reducer's reach.
Worth mentioning if you get asked technical questions about the build —
it's a legitimate LangGraph detail, not a beginner mistake.

## Where n8n fits (not re-implemented here)

In production, the Report Generator's output is what an n8n workflow
would consume to fan out notifications (Slack/email/WhatsApp) and
write to a dashboard DB. That's automation/integration, not agent
reasoning, which is why it's kept separate from the LangGraph agent
logic — matches the "n8n workflows for automation & integrations"
point from the critique.
