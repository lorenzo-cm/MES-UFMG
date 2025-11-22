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

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with specific status"""
        return [task for task in self.tasks.values() if task.status == status]

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

    # GOD METHOD - Does too many things
    def generate_comprehensive_project_report(self, project_id: int) -> Dict:
        """Generate comprehensive project report with all statistics and analysis"""
        project = self.get_project(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Calculate basic stats
        total_tasks = len(project.tasks)
        completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.DONE])
        in_progress_tasks = len([t for t in project.tasks if t.status == TaskStatus.IN_PROGRESS])
        todo_tasks = len([t for t in project.tasks if t.status == TaskStatus.TODO])
        cancelled_tasks = len([t for t in project.tasks if t.status == TaskStatus.CANCELLED])
        
        # Calculate progress percentage
        if total_tasks > 0:
            progress = (completed_tasks / total_tasks) * 100
        else:
            progress = 0
        
        # Calculate priority distribution
        low_priority = len([t for t in project.tasks if t.priority == TaskPriority.LOW])
        medium_priority = len([t for t in project.tasks if t.priority == TaskPriority.MEDIUM])
        high_priority = len([t for t in project.tasks if t.priority == TaskPriority.HIGH])
        critical_priority = len([t for t in project.tasks if t.priority == TaskPriority.CRITICAL])
        
        # Find overdue tasks (assuming deadline is in task)
        overdue_count = 0
        for task in project.tasks:
            if task.status != TaskStatus.DONE and hasattr(task, 'deadline'):
                if task.deadline and datetime.now() > task.deadline:
                    overdue_count += 1
        
        # Calculate member statistics
        member_task_counts = {}
        for member in project.members:
            member_tasks = [t for t in project.tasks if t.assigned_to == member]
            member_task_counts[member.user_id] = {
                "name": member.name,
                "total": len(member_tasks),
                "completed": len([t for t in member_tasks if t.status == TaskStatus.DONE]),
                "in_progress": len([t for t in member_tasks if t.status == TaskStatus.IN_PROGRESS])
            }
        
        # Find most active member
        most_active_member = None
        max_tasks = 0
        for member_id, stats in member_task_counts.items():
            if stats["total"] > max_tasks:
                max_tasks = stats["total"]
                most_active_member = stats["name"]
        
        # Calculate average task completion time
        completion_times = []
        for task in project.tasks:
            if task.status == TaskStatus.DONE and task.completed_at:
                time_diff = (task.completed_at - task.created_at).days
                completion_times.append(time_diff)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Identify bottlenecks (tasks in progress for too long)
        bottlenecks = []
        for task in project.tasks:
            if task.status == TaskStatus.IN_PROGRESS:
                days_in_progress = (datetime.now() - task.updated_at).days
                if days_in_progress > 7:
                    bottlenecks.append({
                        "task_id": task.task_id,
                        "title": task.title,
                        "days_stuck": days_in_progress
                    })
        
        # Calculate risk score
        risk_score = 0
        if progress < 30:
            risk_score += 3
        if overdue_count > total_tasks * 0.2:
            risk_score += 2
        if len(bottlenecks) > 3:
            risk_score += 2
        if critical_priority > 0 and completed_tasks == 0:
            risk_score += 3
        
        # Generate recommendations
        recommendations = []
        if progress < 50 and (datetime.now() - project.created_at).days > 30:
            recommendations.append("Project is behind schedule. Consider adding more resources.")
        if overdue_count > 0:
            recommendations.append(f"{overdue_count} overdue tasks need immediate attention.")
        if len(bottlenecks) > 0:
            recommendations.append(f"{len(bottlenecks)} tasks are stuck in progress. Review blockers.")
        if critical_priority > medium_priority + low_priority:
            recommendations.append("Too many critical tasks. Re-evaluate priorities.")
        
        # Build comprehensive report
        report = {
            "project_id": project.project_id,
            "project_name": project.name,
            "owner": project.owner.name,
            "created_at": project.created_at.isoformat(),
            "task_summary": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "todo": todo_tasks,
                "cancelled": cancelled_tasks,
                "overdue": overdue_count
            },
            "progress_percentage": round(progress, 2),
            "priority_distribution": {
                "low": low_priority,
                "medium": medium_priority,
                "high": high_priority,
                "critical": critical_priority
            },
            "member_statistics": member_task_counts,
            "most_active_member": most_active_member,
            "avg_completion_days": round(avg_completion_time, 1),
            "bottlenecks": bottlenecks,
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score >= 7 else "MEDIUM" if risk_score >= 4 else "LOW",
            "recommendations": recommendations,
            "report_generated_at": datetime.now().isoformat()
        }
        
        return report
