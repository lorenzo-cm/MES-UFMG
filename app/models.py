from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = datetime.now()
        self.tasks: List['Task'] = []

    def get_active_tasks(self):
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def get_completed_tasks(self):
        return [task for task in self.tasks if task.status == TaskStatus.DONE]

    def __repr__(self):
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}')"


class Task:
    def __init__(
        self,
        task_id: int,
        title: str,
        description: str,
        assigned_to: Optional[User] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.priority = priority
        self.status = TaskStatus.TODO
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.tags: List[str] = []

    def assign_to(self, user: User):
        self.assigned_to = user
        self.updated_at = datetime.now()
        if user:
            user.tasks.append(self)

    def update_status(self, status: TaskStatus):
        self.status = status
        self.updated_at = datetime.now()
        if status == TaskStatus.DONE:
            self.completed_at = datetime.now()

    def set_priority(self, priority: TaskPriority):
        self.priority = priority
        self.updated_at = datetime.now()

    def is_overdue(self, deadline: datetime) -> bool:
        if self.status == TaskStatus.DONE:
            return False
        return datetime.now() > deadline

    def __repr__(self):
        return f"Task(id={self.task_id}, title='{self.title}', status={self.status.value})"


class TagManager:
    def __init__(self):
        self.all_tags: List[str] = []

    def add_tag_to_task(self, task: Task, tag: str):
        if tag not in task.tags:
            task.tags.append(tag)
            task.updated_at = datetime.now()
        if tag not in self.all_tags:
            self.all_tags.append(tag)

    def infer_priority_tags(self, task: Task):
        if task.priority == TaskPriority.HIGH:
            self.add_tag_to_task(task, "high_priority")
        elif task.priority == TaskPriority.CRITICAL:
            self.add_tag_to_task(task, "critical")
        elif task.priority == TaskPriority.MEDIUM:
            self.add_tag_to_task(task, "medium_priority")
        elif task.priority == TaskPriority.LOW:
            self.add_tag_to_task(task, "low_priority")
        else:
            self.add_tag_to_task(task, "unknown_priority")

    def infer_status_tags(self, task: Task):
        if task.status == TaskStatus.TODO:
            self.add_tag_to_task(task, "todo")
        elif task.status == TaskStatus.IN_PROGRESS:
            self.add_tag_to_task(task, "in_progress")
        elif task.status == TaskStatus.DONE:
            self.add_tag_to_task(task, "done")
        elif task.status == TaskStatus.CANCELLED:
            self.add_tag_to_task(task, "cancelled")
        else:
            self.add_tag_to_task(task, "unknown_status")

    def remove_tag_from_task(self, task: Task, tag: str):
        if tag in task.tags:
            task.tags.remove(tag)
            task.updated_at = datetime.now()

    def get_task_tags(self, task: Task) -> List[str]:
        return task.tags

    def has_tag(self, task: Task, tag: str) -> bool:
        return tag in task.tags

    def get_tasks_with_tag(self, tasks: List[Task], tag: str) -> List[Task]:
        return [task for task in tasks if tag in task.tags]

    def get_all_tags(self) -> List[str]:
        return self.all_tags

    def get_tasks_by_tag_and_status(self, tasks: List[Task], tag: str, status: TaskStatus) -> List[Task]:
        return [task for task in tasks if tag in task.tags and task.status == status]

    def get_tasks_by_tag_and_priority(self, tasks: List[Task], tag: str, priority: TaskPriority) -> List[Task]:
        return [task for task in tasks if tag in task.tags and task.priority == priority]

    def get_tasks_by_tag_and_assignee(self, tasks: List[Task], tag: str, user: User) -> List[Task]:
        return [task for task in tasks if tag in task.tags and task.assigned_to == user]

    def count_tasks_with_tag(self, tasks: List[Task], tag: str) -> int:
        return len([task for task in tasks if tag in task.tags])

    def get_most_used_tags(self, tasks: List[Task], limit: int = 5) -> List[str]:
        tag_counts = {}
        for task in tasks:
            for tag in task.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:limit]]


class Project:
    def __init__(self, project_id: int, name: str, description: str, owner: User):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.owner = owner
        self.tasks: List[Task] = []
        self.members: List[User] = [owner]
        self.created_at = datetime.now()

    def add_task(self, task: Task):
        self.tasks.append(task)

    def add_member(self, user: User):
        if user not in self.members:
            self.members.append(user)

    def remove_member(self, user: User):
        if user in self.members and user != self.owner:
            self.members.remove(user)

    def get_tasks_by_status(self, status: TaskStatus):
        return [task for task in self.tasks if task.status == status]

    def get_progress(self):
        if not self.tasks:
            return 0.0
        completed = len([t for t in self.tasks if t.status == TaskStatus.DONE])
        return (completed / len(self.tasks)) * 100

    def __repr__(self):
        return f"Project(id={self.project_id}, name='{self.name}', tasks={len(self.tasks)})"
