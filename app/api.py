from typing import Dict, List, Optional
from services import UserService, TaskService, ProjectService
from models import TaskStatus, TaskPriority
from utils import validate_email, sanitize_string
import json


class APIResponse:
    @staticmethod
    def success(data: any, message: str = "Success") -> Dict:
        return {
            "status": "success",
            "message": message,
            "data": data
        }

    @staticmethod
    def error(message: str, code: int = 400) -> Dict:
        return {
            "status": "error",
            "message": message,
            "code": code
        }


class UserAPI:
    def __init__(self, user_service: UserService):
        self.service = user_service

    def create_user(self, name: str, email: str) -> Dict:
        if not name or not email:
            return APIResponse.error("Name and email are required")
        
        if not validate_email(email):
            return APIResponse.error("Invalid email format")
        
        if self.service.find_by_email(email):
            return APIResponse.error("Email already exists")
        
        name = sanitize_string(name)
        user = self.service.create_user(name, email)
        
        return APIResponse.success({
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        }, "User created successfully")

    def get_user(self, user_id: int) -> Dict:
        user = self.service.get_user(user_id)
        if not user:
            return APIResponse.error("User not found", 404)
        
        return APIResponse.success({
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "tasks_count": len(user.tasks)
        })

    def list_users(self) -> Dict:
        users = self.service.get_all_users()
        user_list = [
            {
                "user_id": u.user_id,
                "name": u.name,
                "email": u.email
            }
            for u in users
        ]
        return APIResponse.success(user_list)

    def delete_user(self, user_id: int) -> Dict:
        if self.service.delete_user(user_id):
            return APIResponse.success(None, "User deleted successfully")
        return APIResponse.error("User not found", 404)

    def get_user_performance_report(self, user_id: int) -> Dict:
        """Generate user performance report"""
        user = self.service.get_user(user_id)
        if not user:
            return APIResponse.error("User not found", 404)
        
        total_tasks = len(user.tasks)
        completed_tasks = len(user.get_completed_tasks())
        active_tasks = len(user.get_active_tasks())
        
        performance_score = 0
        if total_tasks > 0:
            performance_score = (completed_tasks / total_tasks) * 100
        
        user_email_domain = user.email.split('@')[1] if '@' in user.email else ''
        user_name_length = len(user.name)
        user_email_length = len(user.email)
        
        high_priority_tasks = sum(1 for t in user.tasks if t.priority.value >= 3)
        low_priority_tasks = sum(1 for t in user.tasks if t.priority.value < 3)
        
        avg_task_duration = 0
        if user.get_completed_tasks():
            total_duration = sum((t.updated_at - t.created_at).days for t in user.get_completed_tasks())
            avg_task_duration = total_duration / len(user.get_completed_tasks())
        
        return APIResponse.success({
            "user_id": user.user_id,
            "user_name": user.name,
            "user_email": user.email,
            "email_domain": user_email_domain,
            "name_length": user_name_length,
            "email_length": user_email_length,
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "active": active_tasks,
            "performance_score": round(performance_score, 2),
            "high_priority_count": high_priority_tasks,
            "low_priority_count": low_priority_tasks,
            "avg_task_duration_days": round(avg_task_duration, 2)
        })


class TaskAPI:
    def __init__(self, task_service: TaskService, user_service: UserService):
        self.service = task_service
        self.user_service = user_service

    def create_task(self, title: str, description: str, assigned_to_id: Optional[int] = None, priority: int = 2) -> Dict:
        if not title:
            return APIResponse.error("Title is required")
        
        title = sanitize_string(title)
        description = sanitize_string(description)
        
        assigned_user = None
        if assigned_to_id:
            assigned_user = self.user_service.get_user(assigned_to_id)
            if not assigned_user:
                return APIResponse.error("Assigned user not found", 404)
        
        task_priority = TaskPriority(priority)
        task = self.service.create_task(title, description, assigned_user, task_priority)
        
        return APIResponse.success({
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value
        }, "Task created successfully")

    def get_task(self, task_id: int) -> Dict:
        task = self.service.get_task(task_id)
        if not task:
            return APIResponse.error("Task not found", 404)
        
        return APIResponse.success({
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": task.assigned_to.user_id if task.assigned_to else None
        })

    def update_status(self, task_id: int, status: str) -> Dict:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            return APIResponse.error("Invalid status")
        
        if self.service.update_task_status(task_id, task_status):
            return APIResponse.success(None, "Task status updated")
        return APIResponse.error("Task not found", 404)

    def list_tasks(self) -> Dict:
        tasks = self.service.get_all_tasks()
        task_list = [
            {
                "task_id": t.task_id,
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value
            }
            for t in tasks
        ]
        return APIResponse.success(task_list)


class ProjectAPI:
    def __init__(self, project_service: ProjectService, user_service: UserService):
        self.service = project_service
        self.user_service = user_service

    def create_project(self, name: str, description: str, owner_id: int) -> Dict:
        if not name:
            return APIResponse.error("Project name is required")
        
        owner = self.user_service.get_user(owner_id)
        if not owner:
            return APIResponse.error("Owner user not found", 404)
        
        name = sanitize_string(name)
        description = sanitize_string(description)
        
        project = self.service.create_project(name, description, owner)
        
        return APIResponse.success({
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "owner_id": owner.user_id
        }, "Project created successfully")

    def get_project(self, project_id: int) -> Dict:
        project = self.service.get_project(project_id)
        if not project:
            return APIResponse.error("Project not found", 404)
        
        return APIResponse.success({
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "tasks_count": len(project.tasks),
            "members_count": len(project.members),
            "progress": project.get_progress()
        })

    def add_task(self, project_id: int, task_id: int, task_service: TaskService) -> Dict:
        task = task_service.get_task(task_id)
        if not task:
            return APIResponse.error("Task not found", 404)
        
        if self.service.add_task_to_project(project_id, task):
            return APIResponse.success(None, "Task added to project")
        return APIResponse.error("Project not found", 404)

    def list_projects(self) -> Dict:
        projects = self.service.get_all_projects()
        project_list = [
            {
                "project_id": p.project_id,
                "name": p.name,
                "tasks_count": len(p.tasks),
                "progress": p.get_progress()
            }
            for p in projects
        ]
        return APIResponse.success(project_list)
