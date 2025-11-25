from typing import Dict, List, Optional
from services import UserService, TaskService, ProjectService
from models import TaskStatus, TaskPriority
from utils import validate_email, sanitize_string
import json
from datetime import datetime


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

    def generate_project_report(self, project_id: int) -> Dict:
        """Generate comprehensive project report"""
        project = self.service.get_project(project_id)
        if not project:
            return APIResponse.error("Project not found", 404)
        
        total_tasks = len(project.tasks)
        if total_tasks == 0:
            return APIResponse.success({"message": "No tasks in project"})
        
        todo_count = 0
        in_progress_count = 0
        done_count = 0
        cancelled_count = 0
        
        for task in project.tasks:
            if task.status == TaskStatus.TODO:
                todo_count += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                in_progress_count += 1
            elif task.status == TaskStatus.DONE:
                done_count += 1
            elif task.status == TaskStatus.CANCELLED:
                cancelled_count += 1
        
        completion_rate = (done_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        low_priority = 0
        medium_priority = 0
        high_priority = 0
        critical_priority = 0
        
        for task in project.tasks:
            if task.priority == TaskPriority.LOW:
                low_priority += 1
            elif task.priority == TaskPriority.MEDIUM:
                medium_priority += 1
            elif task.priority == TaskPriority.HIGH:
                high_priority += 1
            elif task.priority == TaskPriority.CRITICAL:
                critical_priority += 1
        
        active_members = set()
        for task in project.tasks:
            if task.assigned_to:
                active_members.add(task.assigned_to.user_id)
        
        member_workload = {}
        for member in project.members:
            member_tasks = [t for t in project.tasks if t.assigned_to and t.assigned_to.user_id == member.user_id]
            member_workload[member.name] = {
                "total": len(member_tasks),
                "done": len([t for t in member_tasks if t.status == TaskStatus.DONE]),
                "in_progress": len([t for t in member_tasks if t.status == TaskStatus.IN_PROGRESS])
            }
        
        overdue_tasks = []
        now = datetime.now()
        for task in project.tasks:
            if task.status != TaskStatus.DONE and task.status != TaskStatus.CANCELLED:
                days_open = (now - task.created_at).days
                if days_open > 30:
                    overdue_tasks.append({
                        "task_id": task.task_id,
                        "title": task.title,
                        "days_open": days_open,
                        "assigned_to": task.assigned_to.name if task.assigned_to else "Unassigned"
                    })
        
        recent_activity = []
        sorted_tasks = sorted(project.tasks, key=lambda t: t.updated_at, reverse=True)
        for task in sorted_tasks[:5]:
            recent_activity.append({
                "task_id": task.task_id,
                "title": task.title,
                "status": task.status.value,
                "updated_at": task.updated_at.isoformat()
            })
        
        high_priority_pending = [t for t in project.tasks if t.priority == TaskPriority.CRITICAL and t.status != TaskStatus.DONE]
        
        recommendations = []
        if completion_rate < 30:
            recommendations.append("Project completion rate is low. Consider reviewing task assignments.")
        if len(overdue_tasks) > 5:
            recommendations.append(f"There are {len(overdue_tasks)} overdue tasks. Prioritize completion.")
        if len(high_priority_pending) > 0:
            recommendations.append(f"{len(high_priority_pending)} critical priority tasks are pending.")
        if len(active_members) < len(project.members) / 2:
            recommendations.append("Less than half of members have assigned tasks.")
        
        return APIResponse.success({
            "project_id": project.project_id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "status_distribution": {
                "todo": todo_count,
                "in_progress": in_progress_count,
                "done": done_count,
                "cancelled": cancelled_count
            },
            "completion_rate": round(completion_rate, 2),
            "priority_distribution": {
                "low": low_priority,
                "medium": medium_priority,
                "high": high_priority,
                "critical": critical_priority
            },
            "member_count": len(project.members),
            "active_members": len(active_members),
            "member_workload": member_workload,
            "overdue_tasks": overdue_tasks,
            "recent_activity": recent_activity,
            "recommendations": recommendations,
            "generated_at": now.isoformat()
        })
