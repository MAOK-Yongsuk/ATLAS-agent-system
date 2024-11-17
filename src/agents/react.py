from src.cors.models import AcademicState
from datetime import datetime, timezone
from typing import Dict, List

class ReActAgent:
  """
    Base class for ReACT-based agents implementing reasoning and action capabilities.

    Features:
    - Tool management for specific actions
    - Few-shot learning examples
    - Structured thought process
    - Action execution framework
  """

  def __init__(self, llm):
      """
      Initialize the ReActAgent with language model and available tools

      Args:
          llm: Language model instance for agent operations
      """
      self.llm = llm
      # Storage for few-shot examples to guide the agent
      self.few_shot_examples = []

      # Dictionary of available tools with their corresponding methods
      self.tools = {
          "search_calendar": self.search_calendar,      # Calendar search functionality
          "analyze_tasks": self.analyze_tasks,          # Task analysis functionality
          "check_learning_style": self.check_learning_style,  # Learning style assessment
          "check_performance": self.check_performance   # Academic performance checking
      }

  async def search_calendar(self, state: AcademicState) -> List[Dict]:
      """
      Search for upcoming calendar events

      Args:
          state (AcademicState): Current academic state

      Returns:
          List[Dict]: List of upcoming calendar events
      """
      # Get events from calendar or empty list if none exist
      events = state["calendar"].get("events", [])
      # Get current time in UTC
      now = datetime.now(timezone.utc)
      # Filter and return only future events
      return [e for e in events if datetime.fromisoformat(e["start"]["dateTime"]) > now]

  async def analyze_tasks(self, state: AcademicState) -> List[Dict]:
      """
      Analyze academic tasks from the current state

      Args:
          state (AcademicState): Current academic state

      Returns:
          List[Dict]: List of academic tasks
      """
      # Return tasks or empty list if none exist
      return state["tasks"].get("tasks", [])

  async def check_learning_style(self, state: AcademicState) -> Dict:
      """
      Retrieve student's learning style and study patterns

      Args:
          state (AcademicState): Current academic state

      Returns:
          Dict: Dictionary containing learning style and study patterns
      """
      # Get user profile from state
      profile = state["profile"]
      # Return learning preferences and study patterns
      return {
          "style": profile.get("learning_preferences", {}).get("learning_style", {}),
          "patterns": profile.get("learning_preferences", {}).get("study_patterns", {})
      }

  async def check_performance(self, state: AcademicState) -> Dict:
      """
      Check current academic performance across courses

      Args:
          state (AcademicState): Current academic state

      Returns:
          Dict: Information about current courses and performance
      """
      # Get user profile from state
      profile = state["profile"]
      # Return current courses information
      return profile.get("academic_info", {}).get("current_courses", [])