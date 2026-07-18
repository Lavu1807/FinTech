from typing import List
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    llm_available: bool = Field(..., description="Is the Mistral API reachable?")
    exports_dir_writable: bool = Field(..., description="Can we write to exports?")


class UploadResponse(BaseModel):
    dataset_name: str = Field(..., description="Uploaded filename")
    rows: int = Field(..., description="Number of rows in the dataset")
    columns: int = Field(..., description="Number of columns in the dataset")
    file_size_bytes: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Status message")


class AnalyzeRequest(BaseModel):
    filename: str = Field(
        ..., description="Name of the file to analyze, must exist in uploads"
    )


class AnalyzeResponse(BaseModel):
    workflow_id: str = Field(..., description="UUID of the started workflow")
    session_id: str = Field(..., description="Session ID for the workflow")
    status: str = Field(..., description="Current status")
    estimated_runtime: float = Field(..., description="Estimated runtime in seconds")


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    current_agent: str
    completed_agents: List[str]
    remaining_agents: List[str]
    runtime: float
    progress_percentage: float


class ErrorResponse(BaseModel):
    error: str
    message: str
