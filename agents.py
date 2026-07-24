"""
EcoLoop AI Multi-Agent System - agents.py

Enhanced Version
----------------
Features:
- Confidence Scores
- Explainable AI
- Cross-Agent Collaboration Support
- Enterprise-style recommendations
"""

import numpy as np


def _zscore(value: float, history_values: list[float]) -> float:
    if len(history_values) < 4:
        return 0.0

    arr = np.array(history_values[-12:])
    std = arr.std() or 1.0
    return float((value - arr.mean()) / std)


def calculate_confidence(z=None, vibration=None, temp=None):
    """
    Returns confidence score (50-99)
    """

    score = 50

    if z is not None:
        score += min(abs(z) * 15, 35)

    if vibration is not None:
        score += min(vibration * 4, 8)

    if temp is not None:
        score += min(max(temp - 60, 0) * 0.5, 8)

    return round(min(score, 99), 1)


# -----------------------------
# Energy Agent
# -----------------------------
def energy_agent(reading: dict, history: list[dict]) -> dict:

    z = _zscore(
        reading["energy_kwh"],
        [h["energy_kwh"] for h in history]
    )

    if abs(z) < 2:
        return {
            "agent": "Energy Agent",
            "is_anomaly": False,
            "finding": None,
            "confidence": 0,
            "reason": None,
            "action": None,
        }

    direction = "Spike" if z > 0 else "Drop"

    return {
        "agent": "Energy Agent",
        "is_anomaly": True,
        "finding": f"Energy {direction}",
        "confidence": calculate_confidence(z=z),
        "reason": [
            f"Energy deviation (Z-score = {z:.2f})",
            "Deviation from historical baseline"
        ],
        "action":
            "Inspect motors, compressors and idle equipment."
    }


# -----------------------------
# Material Agent
# -----------------------------
def material_agent(reading: dict, history: list[dict]) -> dict:

    z = _zscore(
        reading["material_units"],
        [h["material_units"] for h in history]
    )

    if z < 2:
        return {
            "agent": "Material Agent",
            "is_anomaly": False,
            "finding": None,
            "confidence": 0,
            "reason": None,
            "action": None,
        }

    return {
        "agent": "Material Agent",
        "is_anomaly": True,
        "finding": "Material Waste Increased",
        "confidence": calculate_confidence(z=z),
        "reason": [
            f"Material deviation (Z-score = {z:.2f})",
            "Usage exceeds historical trend"
        ],
        "action":
            "Inspect production line for defects, leakage or excessive consumption."
    }


# -----------------------------
# Maintenance Agent
# -----------------------------
def maintenance_agent(
    reading: dict,
    history: list[dict],
    previous_findings=None
) -> dict:

    vibration = reading["vibration_mm_s"]
    temperature = reading["temp_c"]

    severity = (
        "Critical"
        if (vibration > 4.0 or temperature > 85)
        else "Elevated"
    )

    explanation = [
        f"Temperature = {temperature}°C",
        f"Vibration = {vibration} mm/s"
    ]

    if previous_findings:
        explanation.extend(previous_findings)

    recommendation = (
        "Immediate inspection and planned downtime."
        if severity == "Critical"
        else
        "Schedule preventive maintenance within 24 hours."
    )

    return {
        "agent": "Maintenance Agent",
        "is_anomaly": True,
        "finding": f"{severity} Equipment Health Risk",
        "confidence": calculate_confidence(
            vibration=vibration,
            temp=temperature
        ),
        "reason": explanation,
        "action": recommendation
    }


# -----------------------------
# ESG Agent
# -----------------------------
def esg_agent(reading: dict, history: list[dict]) -> dict:

    if not history:
        return {
            "agent": "ESG Agent",
            "is_anomaly": False,
            "finding": None,
            "confidence": 0,
            "reason": None,
            "action": None,
        }

    energies = [h["energy_kwh"] for h in history]
    energies.append(reading["energy_kwh"])

    materials = [h["material_units"] for h in history]
    materials.append(reading["material_units"])

    total_energy = sum(energies)
    total_material = sum(materials)

    return {
        "agent": "ESG Agent",
        "is_anomaly": False,
        "finding": "Daily Sustainability Summary",
        "confidence": 100,
        "reason": [
            "Daily operational data aggregated",
            "Prepared for ESG reporting"
        ],
        "action":
            f"ESG Report Ready | Total Energy: {total_energy:.0f} kWh | "
            f"Total Material: {total_material:.0f} units | "
            f"Readings: {len(energies)}"
    }