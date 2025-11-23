from services import UserService, TaskService, ProjectService
from api import UserAPI, TaskAPI, ProjectAPI, NotificationAPI
from models import TaskStatus, TaskPriority
from utils import generate_task_summary, format_datetime
from notification_service import NotificationService
import json


def initialize_services():
    """Initialize all services"""
    user_service = UserService()
    task_service = TaskService()
    project_service = ProjectService()
    notification_service = NotificationService()
    
    return user_service, task_service, project_service, notification_service


def initialize_apis(user_service, task_service, project_service, notification_service):
    """Initialize all API handlers"""
    user_api = UserAPI(user_service)
    task_api = TaskAPI(task_service, user_service, notification_service)
    project_api = ProjectAPI(project_service, user_service)
    notification_api = NotificationAPI(notification_service)
    
    return user_api, task_api, project_api, notification_api


def demo_workflow():
    """Demonstrate the task management system"""
    print("=== Task Management System Demo ===\n")
    
    # Initialize services and APIs
    user_service, task_service, project_service, notification_service = initialize_services()
    user_api, task_api, project_api, notification_api = initialize_apis(
        user_service, task_service, project_service, notification_service
    )
    
    # Create users
    print("Creating users...")
    response1 = user_api.create_user("Alice Johnson", "alice@example.com")
    print(json.dumps(response1, indent=2))
    
    response2 = user_api.create_user("Bob Smith", "bob@example.com")
    print(json.dumps(response2, indent=2))
    
    # Create tasks
    print("\nCreating tasks...")
    task1_response = task_api.create_task(
        "Implement authentication",
        "Add JWT authentication to the API",
        assigned_to_id=1,
        priority=4
    )
    print(json.dumps(task1_response, indent=2))
    
    task2_response = task_api.create_task(
        "Write documentation",
        "Document all API endpoints",
        assigned_to_id=2,
        priority=2
    )
    print(json.dumps(task2_response, indent=2))
    
    task3_response = task_api.create_task(
        "Setup CI/CD",
        "Configure GitHub Actions for deployment",
        assigned_to_id=1,
        priority=3
    )
    print(json.dumps(task3_response, indent=2))
    
    # Create project
    print("\nCreating project...")
    project_response = project_api.create_project(
        "API Development",
        "Build REST API for task management",
        owner_id=1
    )
    print(json.dumps(project_response, indent=2))
    
    # Add tasks to project
    print("\nAdding tasks to project...")
    project_api.add_task(1, 1, task_service)
    project_api.add_task(1, 2, task_service)
    project_api.add_task(1, 3, task_service)
    
    # Update task status
    print("\nUpdating task statuses...")
    task_api.update_status(1, "in_progress")
    task_api.update_status(2, "done")
    
    # Get project details
    print("\nProject details:")
    project_details = project_api.get_project(1)
    print(json.dumps(project_details, indent=2))
    
    # List all tasks
    print("\nAll tasks:")
    all_tasks = task_api.list_tasks()
    print(json.dumps(all_tasks, indent=2))
    
    # Generate task summary
    print("\nTask summary:")
    tasks = task_service.get_all_tasks()
    summary = generate_task_summary(tasks)
    print(json.dumps(summary, indent=2))
    
    # Get high priority tasks
    print("\nHigh priority tasks:")
    high_priority = task_service.get_high_priority_tasks()
    for task in high_priority:
        print(f"  - {task.title} (Priority: {task.priority.value})")
    
    # Show notification log
    print("\nNotification log:")
    notification_log = notification_api.get_notification_log()
    print(json.dumps(notification_log, indent=2))


def main():
    """Main entry point"""
    try:
        demo_workflow()
    except Exception as e:
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
