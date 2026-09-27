import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def _rule_based_suggestion(assignment):
    days = assignment["remaining_days"]
    hours = float(assignment["estimated_hours"])
    status = assignment["status"]
    effort_note = (
        f" The {hours:g} estimated hours are substantial for the available time."
        if days <= 2 and hours >= 4
        else f" Plan around the {hours:g} estimated hours."
    )
    if status == "Completed":
        return "This assignment is complete, so it does not need active work scheduling."
    if days < 0:
        timing = f"It is {abs(days)} day{'s' if abs(days) != 1 else ''} overdue."
    elif days == 0:
        timing = "It is due today."
    else:
        timing = f"It is due in {days} day{'s' if days != 1 else ''}."
    level = "high" if assignment["priority_score"] >= 6 else "medium" if assignment["priority_score"] >= 4 else "low"
    status_note = " It is already in progress." if status == "In Progress" else " It is still pending."
    return (
        f"{assignment['difficulty']} difficulty and the deadline mean this has {level} priority. "
        f"{timing}{effort_note}{status_note}"
    )


def suggest_priority(assignment):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"mode": "Demo Rule-Based", "suggestion": _rule_based_suggestion(assignment)}

    endpoint = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (
        "Give a concise, practical student-facing priority suggestion in 1-2 sentences. "
        "Consider difficulty, remaining days (negative means overdue), estimated hours, "
        "status, and this project-defined score. Do not claim certainty. Assignment: "
        + json.dumps({key: assignment[key] for key in (
            "name", "difficulty", "remaining_days", "estimated_hours", "status", "priority_score"
        )})
    )
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = result["choices"][0]["message"]["content"].strip()
        if not text:
            raise ValueError("The LLM returned an empty suggestion.")
        return {"mode": f"LLM: {model}", "suggestion": text}
    except (URLError, TimeoutError, ValueError, KeyError, IndexError, json.JSONDecodeError):
        return {
            "mode": "Demo Rule-Based (LLM unavailable)",
            "suggestion": _rule_based_suggestion(assignment),
        }