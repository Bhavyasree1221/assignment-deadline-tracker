import sqlite3
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from ai_priority import suggest_priority
from data_structures import stack_recent_activity
from database import (
    assignment_counts,
    delete_assignment,
    get_assignment,
    list_assignments,
    log_activity,
    recent_activity,
    save_assignment,
)
from priority import annotate_assignments, prioritize_assignments


app = Flask(__name__)
app.secret_key = "assignment-tracker-local-session"

SUBJECTS = ("Programming", "Data Structures", "Communicative English")
DIFFICULTIES = ("Easy", "Medium", "Hard")
STATUSES = ("Pending", "In Progress", "Completed")


@app.errorhandler(sqlite3.Error)
def handle_database_error(error):
    app.logger.exception("Database operation failed", exc_info=error)
    return render_template("database_error.html"), 503


def activity_stack():
    return stack_recent_activity(recent_activity())


def assignment_form_values(form):
    name = form.get("name", "").strip()
    subject = form.get("subject", "").strip()
    description = form.get("description", "").strip()
    difficulty = form.get("difficulty", "")
    deadline = form.get("deadline", "")
    status = form.get("status", "")
    hours_text = form.get("estimated_hours", "").strip()

    if not name or not subject or not deadline or not hours_text:
        raise ValueError("Fill in each required field before saving.")
    if len(name) > 120 or len(subject) > 80 or len(description) > 1000:
        raise ValueError("Name, subject, or description exceeds the allowed length.")
    if difficulty not in DIFFICULTIES or status not in STATUSES:
        raise ValueError("Choose a valid difficulty and status.")
    try:
        parsed_deadline = date.fromisoformat(deadline)
    except ValueError as error:
        raise ValueError("Enter a valid deadline date.") from error
    try:
        hours = float(hours_text)
    except ValueError as error:
        raise ValueError("Estimated hours must be a number greater than zero.") from error
    if not 0 < hours <= 1000:
        raise ValueError("Estimated hours must be greater than 0 and no more than 1000.")
    return (name, subject, description, difficulty, parsed_deadline.isoformat(), hours, status)


@app.context_processor
def inject_navigation_data():
    return {"subjects": SUBJECTS}


@app.get("/")
def dashboard():
    assignments = list_assignments()
    priority_list = prioritize_assignments(assignments)
    counts = assignment_counts()
    counts["high_priority"] = sum(item["priority_score"] >= 6 for item in priority_list)
    return render_template(
        "dashboard.html",
        counts=counts,
        priority_list=priority_list[:4],
        upcoming=sorted(
            (item for item in annotate_assignments(assignments) if item["status"] != "Completed"),
            key=lambda item: (item["deadline"], item["name"].casefold()),
        )[:5],
        activities=activity_stack()[:5],
    )


@app.route("/assignments/new", methods=["GET", "POST"])
def add_assignment():
    if request.method == "POST":
        try:
            values = assignment_form_values(request.form)
            assignment_id = save_assignment(values)
            log_activity("Added", values[0])
            flash("Assignment added to your tracker.", "success")
            return redirect(url_for("view_assignment", assignment_id=assignment_id))
        except ValueError as error:
            flash(str(error), "error")
        except sqlite3.Error:
            flash("The assignment could not be saved. Please try again.", "error")
    return render_template(
        "assignment_form.html", assignment=None, page_title="Add assignment", form_action="add_assignment"
    )


@app.get("/assignments")
def assignments():
    all_assignments = annotate_assignments(list_assignments())
    query = request.args.get("q", "").strip().casefold()
    subject = request.args.get("subject", "")
    difficulty = request.args.get("difficulty", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    deadline_state = request.args.get("deadline_state", "")
    filtered = [
        item for item in all_assignments
        if (not query or query in item["name"].casefold() or query in item["subject"].casefold()
            or query in item["description"].casefold())
        and (not subject or item["subject"] == subject)
        and (not difficulty or item["difficulty"] == difficulty)
        and (not status or item["status"] == status)
        and (not priority or item["priority_level"] == priority)
        and (not deadline_state or (
            deadline_state == "overdue" and item["remaining_days"] < 0 and item["status"] != "Completed"
        ) or (
            deadline_state == "soon" and 0 <= item["remaining_days"] <= 3 and item["status"] != "Completed"
        ))
    ]
    return render_template(
        "assignments.html",
        assignments=filtered,
        filters={"q": request.args.get("q", ""), "subject": subject, "difficulty": difficulty,
                 "status": status, "priority": priority, "deadline_state": deadline_state},
        difficulties=DIFFICULTIES,
        statuses=STATUSES,
        priority_levels=("High", "Medium", "Low"),
    )


@app.route("/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
def edit_assignment(assignment_id):
    assignment = get_assignment(assignment_id)
    if assignment is None:
        flash("That assignment no longer exists.", "error")
        return redirect(url_for("assignments"))
    if request.method == "POST":
        try:
            values = assignment_form_values(request.form)
            save_assignment(values, assignment_id)
            log_activity("Updated", values[0])
            flash("Assignment changes saved.", "success")
            return redirect(url_for("view_assignment", assignment_id=assignment_id))
        except ValueError as error:
            flash(str(error), "error")
        except sqlite3.Error:
            flash("The assignment could not be updated. Please try again.", "error")
    return render_template(
        "assignment_form.html", assignment=assignment, page_title="Edit assignment", form_action="edit_assignment"
    )


@app.post("/assignments/<int:assignment_id>/delete")
def remove_assignment(assignment_id):
    assignment = get_assignment(assignment_id)
    if assignment and delete_assignment(assignment_id):
        log_activity("Deleted", assignment["name"])
        flash("Assignment deleted.", "success")
    else:
        flash("That assignment no longer exists.", "error")
    return redirect(request.referrer or url_for("assignments"))


@app.get("/assignments/<int:assignment_id>")
def view_assignment(assignment_id):
    assignment = get_assignment(assignment_id)
    if not assignment:
        flash("That assignment no longer exists.", "error")
        return redirect(url_for("assignments"))
    item = annotate_assignments([assignment])[0]
    return render_template("assignment_detail.html", assignment=item)


@app.get("/priority")
def priority_page():
    return render_template("priority.html", assignments=prioritize_assignments(list_assignments()))


@app.get("/ai-priority")
def ai_priority_page():
    active = prioritize_assignments(list_assignments())
    suggestions = [{**item, **suggest_priority(item)} for item in active]
    mode = suggestions[0]["mode"] if suggestions else (
        "LLM configured" if __import__("os").getenv("OPENAI_API_KEY") else "Demo Rule-Based"
    )
    return render_template("ai_priority.html", assignments=suggestions, ai_mode=mode)


@app.get("/data-structures")
def data_structures_page():
    assignments = list_assignments()
    return render_template(
        "data_structures.html",
        assignments=annotate_assignments(assignments)[:5],
        priority_list=prioritize_assignments(assignments)[:4],
        activities=activity_stack()[:5],
        total=len(assignments),
    )


@app.get("/academic-subjects")
def academic_subjects():
    return render_template("subjects.html")


if __name__ == "__main__":
    app.run(debug=True)