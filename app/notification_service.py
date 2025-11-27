from typing import Optional, Dict, List
from models import User, Task, TaskStatus
from datetime import datetime
import json


class NotificationService:
    def __init__(self):
        self.notification_log: List[Dict] = []
        self.smtp_enabled = True
        self.smtp_host = "smtp.example.com"
        self.smtp_port = 587
        self.smtp_user = "noreply@example.com"
        self.smtp_password = "password123"

    def send_task_notification(self, user: User, task: Task, notification_type: str, old_status: Optional[TaskStatus] = None, old_priority: Optional[int] = None) -> Dict:
        """
        Send notification email to user about task changes.
        This method contains all logic: validation, formatting, sending, and logging.
        """
        # Validation section
        if not user:
            error_msg = "User is required for notification"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_msg,
                "user_id": None,
                "task_id": None
            })
            return {"success": False, "error": error_msg}
        
        if not task:
            error_msg = "Task is required for notification"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_msg,
                "user_id": user.user_id if user else None,
                "task_id": None
            })
            return {"success": False, "error": error_msg}
        
        if not user.email:
            error_msg = f"User {user.user_id} has no email address"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_msg,
                "user_id": user.user_id,
                "task_id": task.task_id if task else None
            })
            return {"success": False, "error": error_msg}
        
        valid_types = ["created", "updated", "assigned", "status_changed", "priority_changed", "completed"]
        if notification_type not in valid_types:
            error_msg = f"Invalid notification type: {notification_type}"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_msg,
                "user_id": user.user_id,
                "task_id": task.task_id
            })
            return {"success": False, "error": error_msg}
        
        # Email formatting section
        subject = ""
        body = ""
        
        if notification_type == "created":
            subject = f"New Task Assigned: {task.title}"
            body = f"Hello {user.name},\n\n"
            body += f"A new task has been assigned to you:\n\n"
            body += f"Task ID: {task.task_id}\n"
            body += f"Title: {task.title}\n"
            body += f"Description: {task.description}\n"
            body += f"Priority: {task.priority.name}\n"
            body += f"Status: {task.status.value}\n"
            body += f"Created at: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            body += "Please review and start working on this task.\n\n"
            body += "Best regards,\nTask Management System"
        
        elif notification_type == "updated":
            subject = f"Task Updated: {task.title}"
            body = f"Hello {user.name},\n\n"
            body += f"The following task has been updated:\n\n"
            body += f"Task ID: {task.task_id}\n"
            body += f"Title: {task.title}\n"
            body += f"Description: {task.description}\n"
            body += f"Priority: {task.priority.name}\n"
            body += f"Status: {task.status.value}\n"
            body += f"Last updated: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            body += "Please check the updated details.\n\n"
            body += "Best regards,\nTask Management System"
        
        elif notification_type == "assigned":
            subject = f"Task Assigned to You: {task.title}"
            body = f"Hello {user.name},\n\n"
            body += f"You have been assigned to a new task:\n\n"
            body += f"Task ID: {task.task_id}\n"
            body += f"Title: {task.title}\n"
            body += f"Description: {task.description}\n"
            body += f"Priority: {task.priority.name}\n"
            body += f"Status: {task.status.value}\n\n"
            body += "Please review and start working on this task.\n\n"
            body += "Best regards,\nTask Management System"
        
        elif notification_type == "status_changed":
            if old_status:
                subject = f"Task Status Changed: {task.title}"
                body = f"Hello {user.name},\n\n"
                body += f"The status of your task has been changed:\n\n"
                body += f"Task ID: {task.task_id}\n"
                body += f"Title: {task.title}\n"
                body += f"Previous Status: {old_status.value}\n"
                body += f"New Status: {task.status.value}\n"
                body += f"Changed at: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                if task.status == TaskStatus.DONE:
                    body += "Congratulations! This task has been completed.\n\n"
                elif task.status == TaskStatus.IN_PROGRESS:
                    body += "This task is now in progress. Keep up the good work!\n\n"
                body += "Best regards,\nTask Management System"
            else:
                error_msg = "Old status is required for status_changed notification"
                self.notification_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "message": error_msg,
                    "user_id": user.user_id,
                    "task_id": task.task_id
                })
                return {"success": False, "error": error_msg}
        
        elif notification_type == "priority_changed":
            if old_priority is not None:
                priority_names = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
                old_priority_name = priority_names.get(old_priority, "UNKNOWN")
                subject = f"Task Priority Changed: {task.title}"
                body = f"Hello {user.name},\n\n"
                body += f"The priority of your task has been changed:\n\n"
                body += f"Task ID: {task.task_id}\n"
                body += f"Title: {task.title}\n"
                body += f"Previous Priority: {old_priority_name}\n"
                body += f"New Priority: {task.priority.name}\n"
                body += f"Changed at: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                if task.priority.value > old_priority:
                    body += "This task has been upgraded to a higher priority. Please prioritize accordingly.\n\n"
                else:
                    body += "This task priority has been lowered.\n\n"
                body += "Best regards,\nTask Management System"
            else:
                error_msg = "Old priority is required for priority_changed notification"
                self.notification_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "message": error_msg,
                    "user_id": user.user_id,
                    "task_id": task.task_id
                })
                return {"success": False, "error": error_msg}
        
        elif notification_type == "completed":
            subject = f"Task Completed: {task.title}"
            body = f"Hello {user.name},\n\n"
            body += f"Congratulations! You have completed the following task:\n\n"
            body += f"Task ID: {task.task_id}\n"
            body += f"Title: {task.title}\n"
            body += f"Description: {task.description}\n"
            body += f"Priority: {task.priority.name}\n"
            if task.completed_at:
                body += f"Completed at: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            body += f"\nGreat job on completing this task!\n\n"
            body += "Best regards,\nTask Management System"
        
        # Email sending section (simulated)
        if not self.smtp_enabled:
            warning_msg = f"SMTP is disabled. Notification would be sent to {user.email}"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "warning",
                "message": warning_msg,
                "user_id": user.user_id,
                "task_id": task.task_id,
                "notification_type": notification_type,
                "subject": subject,
                "email": user.email
            })
            return {"success": False, "error": "SMTP is disabled"}
        
        # Simulate SMTP connection and sending
        try:
            email_sent = True
            smtp_response = "250 OK"
            
            if email_sent:
                # Logging section
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "success",
                    "message": f"Notification sent successfully to {user.email}",
                    "user_id": user.user_id,
                    "user_email": user.email,
                    "task_id": task.task_id,
                    "task_title": task.title,
                    "notification_type": notification_type,
                    "subject": subject,
                    "smtp_response": smtp_response,
                    "email_length": len(body)
                }
                self.notification_log.append(log_entry)
                
                return {
                    "success": True,
                    "message": "Notification sent successfully",
                    "user_id": user.user_id,
                    "task_id": task.task_id,
                    "notification_type": notification_type,
                    "email": user.email,
                    "subject": subject
                }
            else:
                error_msg = f"Failed to send email to {user.email}"
                self.notification_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "message": error_msg,
                    "user_id": user.user_id,
                    "task_id": task.task_id,
                    "notification_type": notification_type,
                    "email": user.email
                })
                return {"success": False, "error": error_msg}
        
        except Exception as e:
            error_msg = f"Exception while sending email: {str(e)}"
            self.notification_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_msg,
                "user_id": user.user_id,
                "task_id": task.task_id,
                "notification_type": notification_type,
                "email": user.email,
                "exception": str(e)
            })
            return {"success": False, "error": error_msg}

    def get_notification_log(self, user_id: Optional[int] = None, task_id: Optional[int] = None) -> List[Dict]:
        """Get notification log entries, optionally filtered by user or task"""
        if user_id is None and task_id is None:
            return self.notification_log
        
        filtered = []
        for entry in self.notification_log:
            if user_id is not None and entry.get("user_id") != user_id:
                continue
            if task_id is not None and entry.get("task_id") != task_id:
                continue
            filtered.append(entry)
        
        return filtered

    def clear_log(self):
        """Clear notification log"""
        self.notification_log.clear()

