"""
EcoLoop AI Multi-Agent System - sensors.py

Simulates the IoT feed each specialist agent draws from:
- energy_kwh / material_units  -> Energy Agent, Material Agent
- vibration_mm_s / temp_c      -> Maintenance Agent (equipment health)
"""

import numpy as np


def sense_reading(rng: np.random.Generator, hour: int, force_anomaly: str | None = None) -> dict:
    shift_factor = 0.4 + 0.6 * max(0, np.sin((hour - 6) / 24 * 2 * np.pi))

    energy = 120 * shift_factor + rng.normal(0, 4)
    material = 60 * shift_factor + rng.normal(0, 2.5)
    vibration = 2.2 + 0.6 * shift_factor + rng.normal(0, 0.15)   # mm/s, healthy baseline
    temp = 55 + 10 * shift_factor + rng.normal(0, 1.5)           # deg C, healthy baseline

    if force_anomaly == "energy_spike":
        energy *= rng.uniform(1.6, 2.2)
    elif force_anomaly == "material_spike":
        material *= rng.uniform(1.6, 2.0)
    elif force_anomaly == "unexpected_drop":
        energy *= 0.3
    elif force_anomaly == "maintenance_risk":
        vibration *= rng.uniform(1.8, 2.5)
        temp += rng.uniform(12, 20)

    return {
        "hour": hour,
        "energy_kwh": round(float(energy), 2),
        "material_units": round(float(material), 2),
        "vibration_mm_s": round(float(vibration), 2),
        "temp_c": round(float(temp), 2),
    }
