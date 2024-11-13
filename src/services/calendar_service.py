from typing import List, Dict, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from data.models import CalendarEvent, CalendarTask, StudySession, AcademicTask
from utils.logger import get_logger

logger = get_logger(__name__)

class CalendarService:
    """Service for managing Google Calendar integration"""
    
    def __init__(self, credentials: Credentials, calendar_id: str = 'primary'):
        self.calendar_id = calendar_id
        self.service = build('calendar', 'v3', credentials=credentials)
        self.tasks_service = build('tasks', 'v1', credentials=credentials)
    
    async def create_study_session(self, session: StudySession) -> StudySession:
        """Create a study session event in calendar"""
        try:
            event_body = {
                'summary': f"Study: {session.calendar_event.summary}",
                'description': self._build_session_description(session),
                'start': session.calendar_event.start.dict(),
                'end': session.calendar_event.end.dict(),
                'location': session.calendar_event.location,
                'extendedProperties': {
                    'private': {
                        'type': 'study_session',
                        'material_ids': ','.join(session.material_ids),
                        'progress': str(session.progress)
                    }
                }
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_body
            ).execute()
            
            session.event_id = created_event['id']
            return session
            
        except HttpError as e:
            logger.error(f"Error creating study session: {str(e)}")
            raise
    
    async def create_academic_task(self, task: AcademicTask) -> AcademicTask:
        """Create an academic task with calendar integration"""
        try:
            task_body = {
                'title': task.calendar_task.title,
                'notes': self._build_task_notes(task),
                'due': task.calendar_task.due,
                'status': task.calendar_task.status
            }
            
            if task.calendar_task.parent:
                task_body['parent'] = task.calendar_task.parent
            
            created_task = self.tasks_service.tasks().insert(
                tasklist='@default',
                body=task_body
            ).execute()
            
            task.task_id = created_task['id']
            return task
            
        except HttpError as e:
            logger.error(f"Error creating academic task: {str(e)}")
            raise
    
    async def get_upcoming_study_sessions(
        self, 
        time_min: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[StudySession]:
        """Retrieve upcoming study sessions"""
        try:
            if not time_min:
                time_min = datetime.utcnow()
                
            events = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                privateExtendedProperty='type=study_session'
            ).execute()
            
            return [
                self._convert_to_study_session(event)
                for event in events.get('items', [])
            ]
            
        except HttpError as e:
            logger.error(f"Error retrieving study sessions: {str(e)}")
            raise
    
    async def get_pending_tasks(self) -> List[AcademicTask]:
        """Retrieve pending academic tasks"""
        try:
            tasks = self.tasks_service.tasks().list(
                tasklist='@default',
                showCompleted=False,
                showHidden=False
            ).execute()
            
            return [
                self._convert_to_academic_task(task)
                for task in tasks.get('items', [])
                if self._is_academic_task(task)
            ]
            
        except HttpError as e:
            logger.error(f"Error retrieving tasks: {str(e)}")
            raise
    
    async def update_session_progress(
        self,
        session_id: str,
        progress: float,
        focus_score: Optional[float] = None
    ) -> StudySession:
        """Update study session progress"""
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=session_id
            ).execute()
            
            # Update extended properties
            ext_props = event.get('extendedProperties', {}).get('private', {})
            ext_props['progress'] = str(progress)
            if focus_score:
                ext_props['focus_score'] = str(focus_score)
            
            event['extendedProperties'] = {'private': ext_props}
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=session_id,
                body=event
            ).execute()
            
            return self._convert_to_study_session(updated_event)
            
        except HttpError as e:
            logger.error(f"Error updating session progress: {str(e)}")
            raise
    
    def _build_session_description(self, session: StudySession) -> str:
        """Build detailed description for study session"""
        description = [
            f"Study Session: {session.calendar_event.summary}",
            "",
            "Materials:",
            *[f"- {mid}" for mid in session.material_ids],
            "",
            f"Progress: {session.progress:.1%}",
        ]
        
        if session.difficulty_rating:
            description.append(f"Difficulty: {session.difficulty_rating}/5")
            
        if session.focus_score:
            description.append(f"Focus Score: {session.focus_score}/5")
            
        return "\n".join(description)
    
    def _build_task_notes(self, task: AcademicTask) -> str:
        """Build detailed notes for academic task"""
        notes = [
            f"Subject: {task.subject}",
            f"Estimated Duration: {task.estimated_duration} minutes",
            f"Priority: {task.priority}",
            "",
            "Dependencies:",
            *[f"- {dep}" for dep in task.dependencies],
            "",
            "Completion Criteria:",
            *[f"- {k}: {'✓' if v else '○'}" for k, v in task.completion_criteria.items()]
        ]
        
        if task.calendar_task.notes:
            notes.extend(["", "Additional Notes:", task.calendar_task.notes])
            
        return "\n".join(notes)
    
    def _convert_to_study_session(self, event: Dict) -> StudySession:
        """Convert calendar event to study session"""
        ext_props = event.get('extendedProperties', {}).get('private', {})
        
        return StudySession(
            event_id=event['id'],
            calendar_event=CalendarEvent(
                id=event['id'],
                summary=event['summary'],
                start=event['start'],
                end=event['end'],
                description=event.get('description'),
                location=event.get('location')
            ),
            material_ids=ext_props.get('material_ids', '').split(','),
            progress=float(ext_props.get('progress', 0)),
            focus_score=float(ext_props.get('focus_score', 0)) if 'focus_score' in ext_props else None
        )
    
    def _convert_to_academic_task(self, task: Dict) -> AcademicTask:
        """Convert calendar task to academic task"""
        # Implementation for converting task format
        pass
    
    def _is_academic_task(self, task: Dict) -> bool:
        """Check if task is an academic task"""
        # Implementation for task type checking
        pass