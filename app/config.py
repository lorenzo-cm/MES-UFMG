# Application configuration constants

class Config:
    """Application configuration"""
    
    # API Settings
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Task settings
    MAX_TASK_TITLE_LENGTH = 200
    MAX_TASK_DESCRIPTION_LENGTH = 2000
    
    # Project settings
    MAX_PROJECT_NAME_LENGTH = 100
    MAX_PROJECT_MEMBERS = 50
    
    # User settings
    MAX_USERNAME_LENGTH = 100
    MIN_PASSWORD_LENGTH = 8
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    
    # Timeouts
    DEFAULT_TIMEOUT = 30


class StatusCodes:
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500


class Messages:
    """Response messages"""
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    USER_NOT_FOUND = "User not found"
    
    TASK_CREATED = "Task created successfully"
    TASK_UPDATED = "Task updated successfully"
    TASK_DELETED = "Task deleted successfully"
    TASK_NOT_FOUND = "Task not found"
    
    PROJECT_CREATED = "Project created successfully"
    PROJECT_UPDATED = "Project updated successfully"
    PROJECT_DELETED = "Project deleted successfully"
    PROJECT_NOT_FOUND = "Project not found"
    
    INVALID_INPUT = "Invalid input data"
    UNAUTHORIZED_ACCESS = "Unauthorized access"
