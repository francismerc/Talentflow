from typing import Literal

from pydantic import BaseModel


class HealthData(BaseModel):
    status: Literal["healthy"]
    version: str


class HealthResponse(BaseModel):
    success: bool
    message: str
    data: HealthData
