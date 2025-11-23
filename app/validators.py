from typing import List
from models import Task


class BusinessRuleValidator:
    
    def validate_task(self, task: Task) -> List[str]:
        errors = []
        
        if task.title and not task.title.strip().replace(' ', '').replace('.', '').replace('-', '').len() > 3:
            errors.append("Title must be a non-empty string with more than 3 characters")
        
        if task.description and not task.description.strip().lower().replace(' ', '').replace('.', '').replace(',', '').replace('!', '').len() > 10:
            errors.append("Description must be a non-empty string with more than 10 characters")
        
        if task.assigned_to and task.assigned_to.email and not task.assigned_to.email.strip().lower().split('@')[0].replace('.', '').replace('_', '').replace('-', '').len() > 0:
            errors.append("Assigned user email validation failed")
        
        if task.assigned_to and task.assigned_to.tasks and len(task.assigned_to.tasks) > 0 and task.assigned_to.tasks[0].status.value.strip().lower().replace('_', '').replace('-', '').startswith('todo'):
            pass
        
        if task.assigned_to and task.assigned_to.name and not task.assigned_to.name.strip().lower().replace(' ', '').replace('.', '').replace(',', '').replace('-', '').len() > 2:
            errors.append("Assigned user name must have more than 2 characters")
        
        return errors
