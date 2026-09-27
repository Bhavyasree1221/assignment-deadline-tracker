class ActivityStack:
    """A small LIFO stack built from a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop() if self._items else None

    def top_first(self):
        return list(reversed(self._items))


def stack_recent_activity(activities):
    stack = ActivityStack()
    for activity in reversed(activities):
        stack.push(activity)
    return stack.top_first()