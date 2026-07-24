from typing import TypedDict, List


class SharedFinding(TypedDict):
    agent: str
    finding: str
    confidence: float
    reason: list
    action: str


class SharedState(TypedDict):
    findings: List[SharedFinding]