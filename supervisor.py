from agents import _zscore


def supervisor_reason(reading, history):

    energy_z = _zscore(
        reading["energy_kwh"],
        [h["energy_kwh"] for h in history]
    )

    material_z = _zscore(
        reading["material_units"],
        [h["material_units"] for h in history]
    )

    score = 0

    if abs(energy_z) > 2:
        score += 1

    if material_z > 2:
        score += 1

    if reading["vibration_mm_s"] > 3.2:
        score += 1

    if reading["temp_c"] > 75:
        score += 1

    if score >= 3:
        return "critical"

    if score == 2:
        return "warning"

    return "normal"