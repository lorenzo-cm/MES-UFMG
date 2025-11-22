from typing import List, Optional, Dict
from models import User, Task, Project, TaskStatus, TaskPriority
from datetime import datetime


class UserService:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.next_id = 1

    def create_user(self, name: str, email: str) -> User:
        user = User(self.next_id, name, email)
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def get_all_users(self) -> List[User]:
        return list(self.users.values())

    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def count_active_users(self) -> int:
        """Count users with at least one active task"""
        return sum(1 for user in self.users.values() if user.get_active_tasks())

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    # FEATURE ENVY - This method is envious of User class data
    def generate_user_performance_summary(self, user: User) -> Dict:
        """Generate performance summary for a user - FEATURE ENVY smell"""
        # Uses way more User data than UserService data
        summary = {
            "user_id": user.user_id,
            "user_name": user.name,
            "user_email": user.email,
            "member_since": user.created_at.strftime("%Y-%m-%d"),
            "total_tasks": len(user.tasks),
            "active_tasks": len(user.get_active_tasks()),
            "completed_tasks": len(user.get_completed_tasks()),
        }
        
        # Calculate completion rate using User's data
        if len(user.tasks) > 0:
            completion_rate = (len(user.get_completed_tasks()) / len(user.tasks)) * 100
        else:
            completion_rate = 0.0
        summary["completion_rate"] = round(completion_rate, 2)
        
        # Analyze task priorities from User's tasks
        priority_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for task in user.tasks:
            if task.priority == TaskPriority.LOW:
                priority_counts["low"] += 1
            elif task.priority == TaskPriority.MEDIUM:
                priority_counts["medium"] += 1
            elif task.priority == TaskPriority.HIGH:
                priority_counts["high"] += 1
            elif task.priority == TaskPriority.CRITICAL:
                priority_counts["critical"] += 1
        summary["priority_distribution"] = priority_counts
        
        # Analyze task statuses from User's tasks
        status_counts = {"todo": 0, "in_progress": 0, "done": 0, "cancelled": 0}
        for task in user.tasks:
            if task.status == TaskStatus.TODO:
                status_counts["todo"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                status_counts["in_progress"] += 1
            elif task.status == TaskStatus.DONE:
                status_counts["done"] += 1
            elif task.status == TaskStatus.CANCELLED:
                status_counts["cancelled"] += 1
        summary["status_distribution"] = status_counts
        
        # Calculate average task age from User's completed tasks
        completed_tasks = user.get_completed_tasks()
        if completed_tasks:
            total_days = 0
            for task in completed_tasks:
                if task.completed_at:
                    days = (task.completed_at - task.created_at).days
                    total_days += days
            avg_completion_days = total_days / len(completed_tasks)
            summary["avg_completion_days"] = round(avg_completion_days, 1)
        else:
            summary["avg_completion_days"] = 0
        
        # Find oldest active task from User's data
        active_tasks = user.get_active_tasks()
        if active_tasks:
            oldest_task = min(active_tasks, key=lambda t: t.created_at)
            summary["oldest_active_task"] = {
                "id": oldest_task.task_id,
                "title": oldest_task.title,
                "days_old": (datetime.now() - oldest_task.created_at).days
            }
        else:
            summary["oldest_active_task"] = None
        
        return summary


class TaskService:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1

    def create_task(
        self,
        title: str,
        description: str,
        assigned_to: Optional[User] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        task = Task(self.next_id, title, description, assigned_to, priority)
        self.tasks[self.next_id] = task
        self.next_id += 1
        if assigned_to:
            task.assign_to(assigned_to)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        task = self.get_task(task_id)
        if task:
            task.update_status(status)
            return True
        return False

    def assign_task(self, task_id: int, user: User) -> bool:
        task = self.get_task(task_id)
        if task:
            task.assign_to(user)
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    def get_tasks_by_user(self, user: User) -> List[Task]:
        return [task for task in self.tasks.values() if task.assigned_to == user]

    def get_high_priority_tasks(self) -> List[Task]:
        return [
            task
            for task in self.tasks.values()
            if task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]
        ]


class ProjectService:
    def __init__(self):
        self.projects: Dict[int, Project] = {}
        self.next_id = 1

    def create_project(self, name: str, description: str, owner: User) -> Project:
        project = Project(self.next_id, name, description, owner)
        self.projects[self.next_id] = project
        self.next_id += 1
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.projects.get(project_id)

    def get_all_projects(self) -> List[Project]:
        return list(self.projects.values())

    def add_task_to_project(self, project_id: int, task: Task) -> bool:
        project = self.get_project(project_id)
        if project:
            project.add_task(task)
            return True
        return False

    def add_member_to_project(self, project_id: int, user: User) -> bool:
        project = self.get_project(project_id)
        if project:
            project.add_member(user)
            return True
        return False

    def get_user_projects(self, user: User) -> List[Project]:
        return [
            project
            for project in self.projects.values()
            if user in project.members
        ]

    def delete_project(self, project_id: int) -> bool:
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False
