from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class CalendarEventTime(BaseModel):
    dateTime: Optional[str] = None
    date: Optional[str] = None

class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: CalendarEventTime
    end: CalendarEventTime
    description: Optional[str] = None
    location: Optional[str] = None

class TaskLink(BaseModel):
    type: str
    description: str
    link: str

class CalendarTask(BaseModel):
    id: str
    title: str
    notes: Optional[str] = None
    due: Optional[str] = None
    status: Literal["needsAction", "completed"]
    updated: str
    position: Optional[str] = None
    parent: Optional[str] = None
    links: Optional[List[TaskLink]] = None

class StudySession(BaseModel):
    event_id: str
    calendar_event: CalendarEvent
    material_ids: List[str]
    progress: float = 0.0
    difficulty_rating: Optional[float] = None
    focus_score: Optional[float] = None
    
class AcademicTask(BaseModel):
    """Extended task for academic work"""
    task_id: str
    calendar_task: CalendarTask
    subject: str
    estimated_duration: int  # in minutes
    priority: int = 1
    dependencies: List[str] = []
    completion_criteria: Dict[str, bool] = {}

## Schema for profile analyzer
class LearningStyle(BaseModel):
    preferred_style: str
    effectiveness_score: float
    
class ADHDProfile(BaseModel):
    focus_duration: int  # minutes
    break_frequency: int  # minutes
    optimal_study_time: str  # time of day
    distractions: List[str]
    
class StudyProfile(BaseModel):
    user_id: str
    learning_style: LearningStyle
    adhd_profile: ADHDProfile
    updated_at: datetime