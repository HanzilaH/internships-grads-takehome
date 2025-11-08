from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ---------- MODELS ----------

# Allows us to parse schedule.json
# 3 properties: users (list of strings), handover_start_at (datetime), handover_interval_days (int > 0)
class Schedule(BaseModel):
    users: List[str] = Field(..., min_length=1)
    handover_start_at: datetime
    handover_interval_days: int = Field(..., gt=0)

# Allows us to parse entries in overrides.json n
# 3 properties: user (string), start_at (datetime), end_at (datetime > start_at)
class Entry(BaseModel):
    user: str
    start_at: datetime
    end_at: datetime

    @field_validator("end_at")
    def validate_end_after_start(cls, end_at, info):
        start_at = info.data.get("start_at")
        if start_at and end_at <= start_at:
            raise ValueError("'end_at' must be after 'start_at'")
        return end_at
    
# ---------- EXCEPTIONS ----------
class ScheduleParsingError(Exception):
    pass