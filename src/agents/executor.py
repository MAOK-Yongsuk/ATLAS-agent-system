from src.cors.models import AcademicState
from typing import Dict
from src.agents.planner import PlannerAgent
from src.agents.note_writer import NoteWriterAgent
from src.agents.advisor import AdvisorAgent
import asyncio

class AgentExecutor:
  """
  A class that manages and executes multiple AI agents concurrently
  for academic task processing
  """

  def __init__(self, llm):
      """
      Initialize the AgentExecutor with a language model and predefined agents

      Args:
          llm: Language model instance for agent operations
      """
      self.llm = llm
      # Dictionary of available agents with their specific roles
      self.agents = {
          "PLANNER": PlannerAgent(llm),    # Handles planning and scheduling
          "NOTEWRITER": NoteWriterAgent(llm),  # Handles note-taking tasks
          "ADVISOR": AdvisorAgent(llm)      # Handles advisory and guidance tasks
      }

  async def execute(self, state: AcademicState) -> Dict:
      """
      Execute multiple agents concurrently based on analysis and requirements

      Args:
          state (AcademicState): Current academic state containing all relevant information

      Returns:
          Dict: Results from all executed agents
      """
      try:
          # Extract analysis results from the state
          analysis = state["results"].get("coordinator_analysis", {})

          # Get list of required agents, default to PLANNER if none specified
          required_agents = analysis.get("required_agents", ["PLANNER"])

          # Get groups of agents that can run concurrently
          concurrent_groups = analysis.get("concurrent_groups", [])

          # Store results from all agent executions
          results = {}

          # Process each concurrent group
          for group in concurrent_groups:
              # Collect valid tasks for current group
              valid_tasks = []
              for agent_name in group:
                  # Only include agents that are both required and available
                  if agent_name in required_agents and agent_name in self.agents:
                      valid_tasks.append(self.agents[agent_name](state))

              # Execute valid tasks concurrently
              if valid_tasks:
                  # Gather results from all tasks in the group
                  group_results = await asyncio.gather(*valid_tasks, return_exceptions=True)

                  # Process and store successful results
                  for agent_name, result in zip(group, group_results):
                      if not isinstance(result, Exception):
                          results[agent_name.lower()] = result

          print("----- agent_outputs -------", results)
          # Return formatted results
          return {"results": {"agent_outputs": results}}

      except Exception as e:
          # Error handling with fallback plan
          print(f"Execution error: {e}")
          return {
              "results": {
                  "agent_outputs": {
                      "planner": {"plan": "Emergency fallback plan"}
                  }
              }
          }