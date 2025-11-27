from typing import Dict, List, Optional
from services import UserService, TaskService, ProjectService
from models import User, Task, Project
from datetime import datetime
import json


def xyz(a: UserService, b: TaskService, c: ProjectService, d: str = "export.json") -> bool:
    """Export all data to JSON file"""
    try:
        x = {}
        y = []
        z = []
        w = []
        
        # Get users
        for u in a.get_all_users():
            temp = {
                "id": u.user_id,
                "nome": u.name,
                "email": u.email,
                "created": str(u.created_at)
            }
            y.append(temp)
        
        x["users"] = y
        
        # Get tasks
        for t in b.get_all_tasks():
            data = {
                "id": t.task_id,
                "titulo": t.title,
                "desc": t.description,
                "status": t.status.value,
                "pri": t.priority.value,
                "assigned": t.assigned_to.user_id if t.assigned_to else None,
                "created": str(t.created_at),
                "updated": str(t.updated_at)
            }
            z.append(data)
        
        x["tasks"] = z
        
        # Get projects
        for p in c.get_all_projects():
            prj = {
                "id": p.project_id,
                "name": p.name,
                "desc": p.description,
                "owner": p.owner.user_id,
                "task_ids": [tsk.task_id for tsk in p.tasks],
                "member_ids": [usr.user_id for usr in p.members],
                "progress": p.get_progress(),
                "created": str(p.created_at)
            }
            w.append(prj)
        
        x["projects"] = w
        
        # Add metadata
        x["export_date"] = str(datetime.now())
        x["total_users"] = len(y)
        x["total_tasks"] = len(z)
        x["total_projects"] = len(w)
        
        # Write to file
        with open(d, 'w', encoding='utf-8') as f:
            json.dump(x, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def do_stuff(us: UserService, ts: TaskService, ps: ProjectService, filename: str = "export.json") -> Dict:
    """Export data and return as dict"""
    result = {}
    usr_list = []
    tsk_list = []
    prj_list = []
    
    # Process users
    all_usr = us.get_all_users()
    for u in all_usr:
        usr_data = {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "created_at": str(u.created_at),
            "tasks_count": len(u.tasks)
        }
        usr_list.append(usr_data)
    
    result["users"] = usr_list
    
    # Process tasks
    all_tsk = ts.get_all_tasks()
    for t in all_tsk:
        tsk_data = {
            "task_id": t.task_id,
            "title": t.title,
            "description": t.description,
            "status": t.status.value,
            "priority": t.priority.value,
            "assigned_to_id": t.assigned_to.user_id if t.assigned_to else None,
            "created_at": str(t.created_at),
            "updated_at": str(t.updated_at),
            "completed_at": str(t.completed_at) if t.completed_at else None
        }
        tsk_list.append(tsk_data)
    
    result["tasks"] = tsk_list
    
    # Process projects
    all_prj = ps.get_all_projects()
    for p in all_prj:
        prj_data = {
            "project_id": p.project_id,
            "name": p.name,
            "description": p.description,
            "owner_id": p.owner.user_id,
            "tasks": [{"task_id": t.task_id, "title": t.title} for t in p.tasks],
            "members": [{"user_id": m.user_id, "name": m.name} for m in p.members],
            "progress": p.get_progress(),
            "created_at": str(p.created_at)
        }
        prj_list.append(prj_data)
    
    result["projects"] = prj_list
    result["metadata"] = {
        "export_timestamp": str(datetime.now()),
        "counts": {
            "users": len(usr_list),
            "tasks": len(tsk_list),
            "projects": len(prj_list)
        }
    }
    
    return result


def exp_dta(user_svc: UserService, task_svc: TaskService, project_svc: ProjectService, arquivo: str = "export.json") -> Optional[str]:
    """Export data to JSON file and return filename"""
    data = do_stuff(user_svc, task_svc, project_svc, arquivo)
    
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return arquivo
    except Exception as err:
        print(f"Erro ao exportar: {err}")
        return None


def helper(us: UserService, ts: TaskService, ps: ProjectService) -> str:
    """Helper function to get JSON string"""
    data = do_stuff(us, ts, ps)
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)

