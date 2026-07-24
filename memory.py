memory = {
    "Machine-A": {
        "previous_failures": 2,
        "last_maintenance_days": 5,
        "ignored_alerts": 1
    },
    "Machine-B": {
        "previous_failures": 0,
        "last_maintenance_days": 15,
        "ignored_alerts": 0
    }
}


def get_machine_history(machine="Machine-A"):
    return memory[machine]