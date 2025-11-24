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


def calculate_task_score(task) -> int:
    """Calculate task score based on multiple criteria"""
    score = 0
    
    if task.priority.value == 1:
        score += 5
    elif task.priority.value == 2:
        score += 10
    elif task.priority.value == 3:
        score += 20
    elif task.priority.value == 4:
        score += 40
    
    if task.status.value == "todo":
        score += 10
    elif task.status.value == "in_progress":
        score += 25
    elif task.status.value == "done":
        score += 50
    elif task.status.value == "cancelled":
        score += 0
    
    days_open = (datetime.now() - task.created_at).days
    if days_open < 7:
        score += 5
    elif days_open < 14:
        score += 10
    elif days_open < 30:
        score += 15
    elif days_open < 60:
        score += 20
    elif days_open < 90:
        score += 25
    else:
        score += 30
    
    if task.assigned_to:
        if len(task.assigned_to.tasks) < 5:
            score += 15
        elif len(task.assigned_to.tasks) < 10:
            score += 10
        elif len(task.assigned_to.tasks) < 15:
            score += 5
        elif len(task.assigned_to.tasks) < 20:
            score += 2
        else:
            score += 0
    else:
        score += 20
    
    if hasattr(task, 'title') and task.title:
        if len(task.title) < 20:
            score += 3
        elif len(task.title) < 50:
            score += 5
        elif len(task.title) < 100:
            score += 2
        else:
            score += 1
    
    if hasattr(task, 'description') and task.description:
        if len(task.description) > 100:
            score += 5
        elif len(task.description) > 50:
            score += 3
        else:
            score += 1
    
    return score
