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

    def transfer_project_ownership(self, project_id: int, new_owner: User) -> bool:
        project = self.get_project(project_id)
        if not project:
            return False
        project.owner = new_owner
        if project_id in self.projects:
            self.projects[project_id] = project
            return True
        return False

    def duplicate_project(self, project_id: int, owner: User) -> Optional[Project]:
        original = self.get_project(project_id)
        if not original:
            return None
        copied = Project(self.next_id, getattr(original, "name", "") + " (copy)", getattr(original, "description", ""), owner)
        self.projects[self.next_id] = copied
        self.next_id += 1
        return copied

    def archive_projects_by_owner(self, owner: User) -> int:
        to_delete = []
        for pid, proj in self.projects.items():
            if getattr(proj, "owner", None) == owner:
                to_delete.append(pid)
        count = 0
        for pid in to_delete:
            if pid in self.projects:
                del self.projects[pid]
                count += 1
        return count

    def remove_project_member(self, project_id: int, user: User) -> bool:
        project = self.get_project(project_id)
        if not project:
            return False
        members = getattr(project, "members", [])
        if user in members:
            members.remove(user)
            project.members = members
            return True
        return False
