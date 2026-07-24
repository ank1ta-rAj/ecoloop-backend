knowledge_base = {
    "Machine-A": {
        "previous_failures": [
            "Bearing Failure",
            "Motor Overheating"
        ],
        "maintenance_history": [
            "Bearing replaced - Jan",
            "Lubrication - March",
            "Inspection - June"
        ],
        "operator_notes": [
            "Frequent overload during night shift"
        ]
    }
}


def retrieve_machine_knowledge(machine="Machine-A"):
    return knowledge_base.get(machine, {})