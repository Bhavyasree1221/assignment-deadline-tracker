from datetime import date

from data_structures import stack_recent_activity
from database import list_assignments, log_activity, recent_activity, save_assignment
from priority import annotate_assignments, prioritize_assignments


def prompt_assignment():
    name = input("Assignment name: ").strip()
    subject = input("Subject: ").strip()
    description = input("Description (optional): ").strip()
    difficulty = input("Difficulty (Easy/Medium/Hard): ").strip().title()
    deadline_text = input("Deadline (YYYY-MM-DD): ").strip()
    hours_text = input("Estimated completion hours: ").strip()
    status = input("Status (Pending/In Progress/Completed): ").strip().title()
    if not name or not subject:
        raise ValueError("Assignment name and subject are required.")
    if difficulty not in ("Easy", "Medium", "Hard"):
        raise ValueError("Difficulty must be Easy, Medium, or Hard.")
    if status not in ("Pending", "In Progress", "Completed"):
        raise ValueError("Status must be Pending, In Progress, or Completed.")
    deadline = date.fromisoformat(deadline_text).isoformat()
    hours = float(hours_text)
    if not 0 < hours <= 1000:
        raise ValueError("Estimated hours must be greater than 0 and no more than 1000.")
    values = (name, subject, description, difficulty, deadline, hours, status)
    assignment_id = save_assignment(values)
    log_activity("Added", name)
    print(f"Saved assignment #{assignment_id}.")


def show_assignments():
    rows = annotate_assignments(list_assignments())
    if not rows:
        print("No assignments yet.")
        return
    for item in rows:
        print(
            f"#{item['id']} {item['name']} | {item['subject']} | {item['status']} | "
            f"{item['remaining_days']} days | score {item['priority_score']} ({item['priority_level']})"
        )


def show_priority_list():
    rows = prioritize_assignments(list_assignments())
    if not rows:
        print("No pending or in-progress assignments to prioritize.")
        return
    for item in rows:
        print(f"#{item['rank']} {item['name']} | score {item['priority_score']} | {item['priority_reason']}")


def show_stack():
    stack = stack_recent_activity(recent_activity())
    if not stack:
        print("No activity recorded yet.")
        return
    for item in stack:
        print(f"{item['action']} {item['assignment_name']} at {item['created_at']}")


def main():
    menu = "\n1. Add Assignment\n2. View Assignments\n3. Show Priority List\n4. Show Recent Stack\n5. Exit"
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                prompt_assignment()
            elif choice == "2":
                show_assignments()
            elif choice == "3":
                show_priority_list()
            elif choice == "4":
                show_stack()
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Choose a number from 1 to 5.")
        except (ValueError, EOFError) as error:
            print(f"Could not save assignment: {error}")


if __name__ == "__main__":
    main()