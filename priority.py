import heapq
from datetime import date


DIFFICULTY_SCORES = {"Easy": 1, "Medium": 2, "Hard": 3}


def remaining_days(deadline, today=None):
    current_date = today or date.today()
    due_date = date.fromisoformat(deadline) if isinstance(deadline, str) else deadline
    return (due_date - current_date).days


def urgency_score(days_left):
    if days_left <= 0:
        return 5
    if days_left <= 2:
        return 4
    if days_left <= 5:
        return 3
    if days_left <= 7:
        return 2
    return 1


def enrich_assignment(assignment, today=None):
    item = dict(assignment)
    days_left = remaining_days(item["deadline"], today)
    difficulty_score = DIFFICULTY_SCORES[item["difficulty"]]
    urgency = urgency_score(days_left)
    score = difficulty_score + urgency
    item.update(
        remaining_days=days_left,
        difficulty_score=difficulty_score,
        urgency_score=urgency,
        priority_score=score,
        priority_level="High" if score >= 6 else "Medium" if score >= 4 else "Low",
        priority_reason=f"{item['difficulty']} difficulty + "
        f"{'overdue or due today' if days_left <= 0 else 'deadline in ' + str(days_left) + ' days'}.",
    )
    return item


def prioritize_assignments(assignments, today=None):
    """Use heapq as a max-priority queue, excluding completed work."""
    heap = []
    for assignment in assignments:
        item = enrich_assignment(assignment, today)
        if item["status"] == "Completed":
            continue
        heapq.heappush(
            heap,
            (-item["priority_score"], item["deadline"], item["name"].casefold(), item["id"], item),
        )
    ordered = []
    while heap:
        item = heapq.heappop(heap)[-1]
        item["rank"] = len(ordered) + 1
        ordered.append(item)
    return ordered


def annotate_assignments(assignments, today=None):
    return [enrich_assignment(item, today) for item in assignments]