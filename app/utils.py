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


def export_json_report(task_service, filepath: str) -> bool:
    import json
    from models import TaskStatus
    
    if not task_service:
        return False
    if not filepath:
        return False
    if not filepath.endswith('.json'):
        filepath = filepath + '.json'
    
    tasks = task_service.get_all_tasks()
    todo_count = 0
    in_progress_count = 0
    done_count = 0
    cancelled_count = 0
    
    for task in tasks:
        if task.status == TaskStatus.TODO:
            todo_count += 1
        elif task.status == TaskStatus.IN_PROGRESS:
            in_progress_count += 1
        elif task.status == TaskStatus.DONE:
            done_count += 1
        elif task.status == TaskStatus.CANCELLED:
            cancelled_count += 1
    
    report_data = {
        "generated_at": format_datetime(datetime.now()),
        "total_tasks": len(tasks),
        "summary": {
            "todo": todo_count,
            "in_progress": in_progress_count,
            "done": done_count,
            "cancelled": cancelled_count
        },
        "tasks": []
    }
    
    for task in tasks:
        task_data = {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value
        }
        if task.assigned_to:
            task_data["assigned_to"] = task.assigned_to.name
        report_data["tasks"].append(task_data)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        return True
    except Exception:
        return False


def export_csv_report(task_service, filepath: str) -> bool:
    import csv
    from models import TaskStatus
    
    if not task_service:
        return False
    if not filepath:
        return False
    if not filepath.endswith('.csv'):
        filepath = filepath + '.csv'
    
    tasks = task_service.get_all_tasks()
    todo_count = 0
    in_progress_count = 0
    done_count = 0
    cancelled_count = 0
    
    for task in tasks:
        if task.status == TaskStatus.TODO:
            todo_count += 1
        elif task.status == TaskStatus.IN_PROGRESS:
            in_progress_count += 1
        elif task.status == TaskStatus.DONE:
            done_count += 1
        elif task.status == TaskStatus.CANCELLED:
            cancelled_count += 1
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Generated At', format_datetime(datetime.now())])
            writer.writerow(['Total Tasks', len(tasks)])
            writer.writerow(['Todo', todo_count])
            writer.writerow(['In Progress', in_progress_count])
            writer.writerow(['Done', done_count])
            writer.writerow(['Cancelled', cancelled_count])
            writer.writerow([])
            writer.writerow(['Task ID', 'Title', 'Status', 'Priority', 'Assigned To'])
            
            for task in tasks:
                assigned_name = ""
                if task.assigned_to:
                    assigned_name = task.assigned_to.name
                writer.writerow([
                    task.task_id,
                    task.title,
                    task.status.value,
                    task.priority.value,
                    assigned_name
                ])
        return True
    except Exception:
        return False