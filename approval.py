def manager_approval(confidence):

    if confidence >= 90:
        return {
            "approved": False,
            "message": "Manager approval required before scheduling maintenance."
        }

    return {
        "approved": True,
        "message": "Auto-approved."
    }