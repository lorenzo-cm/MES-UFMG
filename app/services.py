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

    def get_recent_users(self, days: int = 7) -> List[User]:
        """Get users created in the last N days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            user for user in self.users.values()
            if user.created_at >= cutoff_date
        ]

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None


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

    # HIGH CYCLOMATIC COMPLEXITY - Too many branches and conditions
    def calculate_task_priority_score(self, task: Task, user: Optional[User] = None) -> int:
        """Calculate priority score for task scheduling with complex business rules"""
        score = 0
        
        # Base priority score
        if task.priority == TaskPriority.CRITICAL:
            score += 100
        elif task.priority == TaskPriority.HIGH:
            score += 50
        elif task.priority == TaskPriority.MEDIUM:
            score += 25
        else:
            score += 10
        
        # Status modifiers
        if task.status == TaskStatus.IN_PROGRESS:
            score += 20
            if task.assigned_to:
                score += 10
                if task.assigned_to.get_active_tasks():
                    if len(task.assigned_to.get_active_tasks()) > 5:
                        score -= 15
                    elif len(task.assigned_to.get_active_tasks()) > 3:
                        score -= 10
                    else:
                        score += 5
        elif task.status == TaskStatus.TODO:
            if task.assigned_to:
                score += 5
            else:
                score += 15
        elif task.status == TaskStatus.DONE:
            score = 0
        else:
            score -= 50
        
        # User-specific adjustments
        if user:
            if task.assigned_to == user:
                score += 30
                if task.priority == TaskPriority.CRITICAL:
                    score += 20
            else:
                if task.assigned_to is None:
                    score += 10
                else:
                    score -= 5
        
        # Time-based modifiers
        days_old = (datetime.now() - task.created_at).days
        if days_old > 30:
            score += 40
            if task.status == TaskStatus.TODO:
                score += 20
                if task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]:
                    score += 30
        elif days_old > 14:
            score += 20
            if task.status == TaskStatus.TODO:
                score += 10
        elif days_old > 7:
            score += 10
        else:
            if task.priority == TaskPriority.CRITICAL:
                score += 15
        
        # Assignment logic
        if task.assigned_to:
            active_tasks = task.assigned_to.get_active_tasks()
            if active_tasks:
                if len(active_tasks) > 10:
                    score -= 30
                elif len(active_tasks) > 7:
                    score -= 20
                elif len(active_tasks) > 5:
                    score -= 10
                else:
                    if task.priority == TaskPriority.CRITICAL:
                        score += 10
        else:
            if task.priority == TaskPriority.CRITICAL:
                score += 25
            elif task.priority == TaskPriority.HIGH:
                score += 15
        
        # Final adjustments
        if score < 0:
            score = 0
        elif score > 200:
            if task.priority == TaskPriority.CRITICAL:
                score = 200
            else:
                score = 150
        
        return score


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

    def count_tasks_by_priority(self, project_id: int) -> Dict[str, int]:
        """Count tasks grouped by priority level"""
        project = self.get_project(project_id)
        if not project:
            return {}
        
        counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        for task in project.tasks:
            if task.priority == TaskPriority.LOW:
                counts["low"] += 1
            elif task.priority == TaskPriority.MEDIUM:
                counts["medium"] += 1
            elif task.priority == TaskPriority.HIGH:
                counts["high"] += 1
            elif task.priority == TaskPriority.CRITICAL:
                counts["critical"] += 1
        
        return counts

    def delete_project(self, project_id: int) -> bool:
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False
