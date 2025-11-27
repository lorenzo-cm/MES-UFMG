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


def validate_task_inputs(title: str, description: str, assigned_to_id: Optional[int], priority: int, max_title_length: int, min_title_length: int, max_description_length: int, min_description_length: int, allow_empty_description: bool, allow_special_chars_title: bool, allow_special_chars_description: bool, require_assigned_user: bool, min_priority_value: int, max_priority_value: int, allow_negative_priority: bool, validate_title_format: bool, validate_description_format: bool, check_title_duplicates: bool, enforce_title_casing: bool, validate_priority_range: bool) -> tuple[bool, Optional[str]]:
    if not title:
        return False, "Title is required"
    
    if len(title) < min_title_length:
        return False, f"Title must be at least {min_title_length} characters"
    
    if len(title) > max_title_length:
        return False, f"Title must not exceed {max_title_length} characters"
    
    if not allow_empty_description and not description:
        return False, "Description is required"
    
    if description and len(description) < min_description_length:
        return False, f"Description must be at least {min_description_length} characters"
    
    if description and len(description) > max_description_length:
        return False, f"Description must not exceed {max_description_length} characters"
    
    if require_assigned_user and not assigned_to_id:
        return False, "Assigned user is required"
    
    if validate_priority_range:
        if priority < min_priority_value or priority > max_priority_value:
            return False, f"Priority must be between {min_priority_value} and {max_priority_value}"
    
    if not allow_negative_priority and priority < 0:
        return False, "Priority cannot be negative"
    
    if validate_title_format and not title[0].isupper():
        return False, "Title must start with uppercase letter"
    
    if not allow_special_chars_title and re.search(r'[<>{}]', title):
        return False, "Title contains invalid special characters"
    
    if not allow_special_chars_description and description and re.search(r'[<>{}]', description):
        return False, "Description contains invalid special characters"
    
    return True, None