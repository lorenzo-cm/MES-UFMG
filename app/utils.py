import re
from typing import Optional
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

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


def generate_task_report(user_id: int, project_id: int, status_filter: str, priority_filter: int, start_date: str, end_date: str, include_archived: bool, sort_by: str) -> dict:
    """Generate comprehensive task report with multiple filters"""
    report = {
        "user_id": user_id,
        "project_id": project_id,
        "filters": {
            "status": status_filter,
            "priority": priority_filter,
            "start_date": start_date,
            "end_date": end_date,
            "include_archived": include_archived,
            "sort_by": sort_by
        },
        "generated_at": format_datetime(datetime.now())
    }
    return report


def format_date_range(start: datetime, end: datetime) -> str:
    """Format date range for display"""
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"