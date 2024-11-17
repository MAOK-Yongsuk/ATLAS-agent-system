from typing import List,  Dict, Annotated, Any, TypedDict
from langchain_core.messages import BaseMessage
from operator import add

class AcademicState(TypedDict):
   """Master state container for the academic assistance system"""
   messages: Annotated[List[BaseMessage], add]   # Conversation history
   profile: dict                                 # Student information
   calendar: dict                                # Scheduled events
   tasks: dict                                   # To-do items and assignments
   results: Dict[str, Any]                       # Operation outputs