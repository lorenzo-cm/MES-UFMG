from pydantic import BaseModel, Field


class CodeSmell(BaseModel):
    """Represents a single code smell detected in the code."""
    file: str = Field(description="Path to the file where the smell was detected (e.g., 'app/test.py')")
    line: int = Field(description="Line number where the smell starts (1-indexed)")
    smell_type: str = Field(description="Type/category of the code smell (e.g., 'TODO_COMMENT', 'UNUSED_VARIABLE', 'MAGIC_NUMBER', etc.)")
    message: str = Field(description="Clear, actionable description of the issue")
    severity: str = Field(description="Severity level: 'INFO', 'MINOR', 'MAJOR', or 'CRITICAL'")


class CodeReviewResponse(BaseModel):
    """Complete code review response with detected smells and general feedback."""
    smells: list[CodeSmell] = Field(description="List of all code smells detected in the PR")
    pr_comment: str = Field(description="General Markdown-formatted comment to be posted on the PR, summarizing the review")
