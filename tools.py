from memory import get_machine_history

from knowledge_base import retrieve_machine_knowledge


def retrieve_history(machine="Machine-A"):
    return retrieve_machine_knowledge(machine)

def fetch_machine_history(machine="Machine-A"):
    return get_machine_history(machine)


def notify_manager(message):
    return f"Notification sent: {message}"


def generate_esg_report(history):
    return {
        "status": "Generated",
        "records": len(history)
    }