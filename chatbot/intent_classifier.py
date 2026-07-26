def get_intent(question):
    
    question = question.lower()

    if "organization" in question or "organisation" in question:
        return "organization"

    if "person" in question or "scientist" in question:
        return "person"

    if "location" in question or "where" in question:
        return "location"

    if "date" in question or "when" in question:
        return "date"

    return "summary"