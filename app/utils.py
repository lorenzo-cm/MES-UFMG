import re
from typing import Optional, List
from datetime import datetime, timedelta


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(text: str) -> str:
    """Remove special characters and extra whitespace"""
    text = re.sub(r'[<>{}]', '', text)
    text = ' '.join(text.split())
    return text.strip()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse string to datetime"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None


def calculate_deadline(days: int) -> datetime:
    """Calculate deadline from today"""
    return datetime.now() + timedelta(days=days)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_task_summary(tasks: list) -> dict:
    """Generate summary statistics for tasks"""
    from models import TaskStatus

    summary = {
        "total": len(tasks),
        "todo": 0,
        "in_progress": 0,
        "done": 0,
        "cancelled": 0
    }

    for task in tasks:
        if task.status == TaskStatus.TODO:
            summary["todo"] += 1
        elif task.status == TaskStatus.IN_PROGRESS:
            summary["in_progress"] += 1
        elif task.status == TaskStatus.DONE:
            summary["done"] += 1
        elif task.status == TaskStatus.CANCELLED:
            summary["cancelled"] += 1

    return summary


def calculate_completion_rate(completed: int, total: int) -> float:
    """Calculate completion rate percentage"""
    if total == 0:
        return 0.0
    return (completed / total) * 100


def is_valid_priority(priority: int) -> bool:
    """Check if priority value is valid"""
    return priority in [1, 2, 3, 4]


def format_user_display_name(name: str, email: str) -> str:
    """Format user display name"""
    return f"{name} ({email})"


def process_bulk_task_actions(
    tasks: List,
    user_email_filter: Optional[str] = None,
    priority_filter: Optional[int] = None,
    escalate_after_days: Optional[int] = None,
    notify: bool = False,
    archive_completed: bool = False,
    export_format: str = "none"
) -> dict:
    from models import TaskStatus, TaskPriority
    import json
    import io
    import csv

    now = datetime.now()
    summary = {
        "processed": 0,
        "skipped": 0,
        "errors": 0,
        "escalated": 0,
        "moved_to_in_progress": 0,
        "auto_completed": 0,
        "notified": 0,
        "archived": 0,
        "cancelled": 0,
    }
    notifications = []
    csv_rows = []

    for t in tasks:
        try:
            should_skip = False
            if user_email_filter:
                assignee = getattr(t, "assigned_to", None)
                email = getattr(assignee, "email", None) if assignee else None
                if not email or user_email_filter not in email:
                    should_skip = True

            if priority_filter is not None:
                p = getattr(t, "priority", None)
                pval = p.value if hasattr(p, "value") else p
                if pval != priority_filter:
                    should_skip = True

            if should_skip:
                summary["skipped"] += 1
                continue

            if t.status == TaskStatus.TODO:
                due = getattr(t, "due_date", None)
                if due:
                    if due < now:
                        if escalate_after_days is not None:
                            delta = now - due
                            if delta.days >= escalate_after_days:
                                try:
                                    t.priority = TaskPriority.CRITICAL
                                    summary["escalated"] += 1
                                except Exception:
                                    pass
                        else:
                            try:
                                t.status = TaskStatus.IN_PROGRESS
                                summary["moved_to_in_progress"] += 1
                            except Exception:
                                pass
                    else:
                        if getattr(t, "reminder_sent", False):
                            if notify and getattr(t, "assigned_to", None) and getattr(t.assigned_to, "email", None):
                                notifications.append({"task_id": getattr(t, "task_id", None), "email": t.assigned_to.email, "type": "reminder"})
                                summary["notified"] += 1
                else:
                    if getattr(t, "priority", None) and getattr(t.priority, "value", 0) >= 3:
                        try:
                            t.status = TaskStatus.IN_PROGRESS
                            summary["moved_to_in_progress"] += 1
                        except Exception:
                            pass

            elif t.status == TaskStatus.IN_PROGRESS:
                prog = getattr(t, "progress", None)
                if prog is not None:
                    try:
                        if prog >= 0.95:
                            t.status = TaskStatus.DONE
                            summary["auto_completed"] += 1
                        else:
                            if notify and getattr(t, "assigned_to", None) and getattr(t.assigned_to, "email", None):
                                notifications.append({"task_id": getattr(t, "task_id", None), "email": t.assigned_to.email, "type": "in_progress_alert"})
                                summary["notified"] += 1
                    except Exception:
                        pass
                else:
                    if notify and getattr(t, "assigned_to", None) and getattr(t.assigned_to, "email", None):
                        notifications.append({"task_id": getattr(t, "task_id", None), "email": t.assigned_to.email, "type": "status_check"})
                        summary["notified"] += 1

            elif t.status == TaskStatus.DONE:
                if archive_completed:
                    try:
                        setattr(t, "archived", True)
                        summary["archived"] += 1
                    except Exception:
                        pass

            elif t.status == TaskStatus.CANCELLED:
                summary["cancelled"] += 1
            else:
                if notify and getattr(t, "assigned_to", None) and getattr(t.assigned_to, "email", None):
                    notifications.append({"task_id": getattr(t, "task_id", None), "email": t.assigned_to.email, "type": "unknown_status"})
                    summary["notified"] += 1

            csv_rows.append({
                "task_id": getattr(t, "task_id", None),
                "title": getattr(t, "title", "") or "",
                "status": getattr(t, "status", None).name if getattr(t, "status", None) else "",
                "priority": getattr(getattr(t, "priority", None), "name", getattr(t, "priority", None))
            })
            summary["processed"] += 1

        except Exception:
            summary["errors"] += 1
            continue

    exported = None
    if export_format == "json":
        exported = json.dumps({"summary": summary, "rows": csv_rows, "notifications": notifications})
    elif export_format == "csv":
        output = io.StringIO()
        fieldnames = ["task_id", "title", "status", "priority"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
        exported = output.getvalue()
    else:
        exported = {"summary": summary, "rows": csv_rows}

    if notify:
        summary["notifications"] = notifications

    summary["exported"] = exported
    return summary
