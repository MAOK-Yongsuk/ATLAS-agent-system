import json
from typing import Dict
from src.cors.models import AcademicState
from src.agents.react import ReActAgent
from datetime import datetime, timezone, timedelta
from langgraph.graph import StateGraph, Graph
# from IPython.display import display, Image

class PlannerAgent(ReActAgent):
  def __init__(self, llm):
      super().__init__(llm)
      self.llm = llm
      # Initialize few shot examples
      self.few_shot_examples = self._initialize_examples()
      # Create and compile workflow
      self.workflow = self.create_graph()

  def _initialize_examples(self):
      return [
          {
              "input": "Help with exam prep while managing ADHD and football",
              "thought": "Need to check calendar conflicts and energy patterns",
              "action": "search_calendar",
              "observation": "Football match at 6PM, exam tomorrow 9AM",
              "plan": """ADHD-OPTIMIZED SCHEDULE:
                  PRE-FOOTBALL (2PM-5PM):
                  - 3x20min study sprints
                  - Movement breaks
                  - Quick rewards after each sprint

                  FOOTBALL MATCH (6PM-8PM):
                  - Use as dopamine reset
                  - Formula review during breaks

                  POST-MATCH (9PM-12AM):
                  - Environment: Café noise
                  - 15/5 study/break cycles
                  - Location changes hourly

                  EMERGENCY PROTOCOLS:
                  - Focus lost → jumping jacks
                  - Overwhelmed → room change
                  - Brain fog → cold shower"""
          },
          {
              "input": "Struggling with multiple deadlines",
              "thought": "Check task priorities and performance issues",
              "action": "analyze_tasks",
              "observation": "3 assignments due, lowest grade in Calculus",
              "plan": """PRIORITY SCHEDULE:
                  HIGH-FOCUS SLOTS:
                  - Morning: Calculus practice
                  - Post-workout: Assignments
                  - Night: Quick reviews

                  ADHD MANAGEMENT:
                  - Task timer challenges
                  - Reward system per completion
                  - Study buddy accountability"""
          }
      ]

  def create_graph(self) -> Graph:
      # Create graph
      workflow = StateGraph(AcademicState)

      # Add nodes
      workflow.add_node("calendar_analyzer", self.calendar_analyzer)
      workflow.add_node("task_analyzer", self.task_analyzer)
      workflow.add_node("plan_generator", self.plan_generator)

      # Define edges
      workflow.add_edge("calendar_analyzer", "task_analyzer")
      workflow.add_edge("task_analyzer", "plan_generator")

      # Set entry point
      workflow.set_entry_point("calendar_analyzer")

      # Compile
      return workflow.compile()

  async def calendar_analyzer(self, state: AcademicState) -> AcademicState:
      """Analyze calendar events"""
      events = state["calendar"].get("events", [])
      now = datetime.now(timezone.utc)
      future = now + timedelta(days=7)

      filtered_events = [
          event for event in events
          if now <= datetime.fromisoformat(event["start"]["dateTime"]) <= future
      ]

      prompt = """Analyze calendar events and identify:
      Events: {events}

      Focus on:
      - Available time blocks
      - Energy impact of activities
      - Potential conflicts
      - Recovery periods
      - Study opportunity windows
      - Activity patterns
      - Schedule optimization
      """

      messages = [
          {"role": "system", "content": prompt},
          {"role": "user", "content": json.dumps(filtered_events)}
      ]

      response = await self.llm.agenerate(messages)
      state["results"]["calendar_analysis"] = response
      return state

  async def task_analyzer(self, state: AcademicState) -> AcademicState:
      """Analyze tasks and priorities"""
      tasks = state["tasks"].get("tasks", [])

      prompt = """Analyze tasks and create priority structure:
      Tasks: {tasks}

      Consider:
      - Urgency levels
      - Task complexity
      - Energy requirements
      - Dependencies
      - Required focus levels
      - Time estimations
      - Learning objectives
      - Success criteria
      """

      messages = [
          {"role": "system", "content": prompt},
          {"role": "user", "content": json.dumps(tasks)}
      ]

      response = await self.llm.agenerate(messages)
      state["results"]["task_analysis"] = response
      return state

  async def plan_generator(self, state: AcademicState) -> AcademicState:
      """Generate final study plan"""
      profile_analysis = state["results"]["profile_analysis"]
      calendar_analysis = state["results"]["calendar_analysis"]
      task_analysis = state["results"]["task_analysis"]

      prompt = f"""AI Planning Assistant: Create focused study plan using ReACT framework.

      INPUT CONTEXT:
      - Profile Analysis: {profile_analysis}
      - Calendar Analysis: {calendar_analysis}
      - Task Analysis: {task_analysis}

      EXAMPLES:
      {json.dumps(self.few_shot_examples, indent=2)}

      INSTRUCTIONS:
      1. Follow ReACT pattern:
        Thought: Analyze situation and needs
        Action: Consider all analyses
        Observation: Synthesize findings
        Plan: Create structured plan

      2. Address:
        - ADHD management strategies
        - Energy level optimization
        - Task chunking methods
        - Focus period scheduling
        - Environment switching tactics
        - Recovery period planning
        - Social/sport activity balance

      3. Include:
        - Emergency protocols
        - Backup strategies
        - Quick wins
        - Reward system
        - Progress tracking
        - Adjustment triggers

      FORMAT:
      Thought: [reasoning and situation analysis]
      Action: [synthesis approach]
      Observation: [key findings]
      Plan: [actionable steps and structural schedule]
      """

      messages = [
          {"role": "system", "content": prompt},
          {"role": "user", "content": state["messages"][-1].content}
      ]

      response = await self.llm.agenerate(messages, temperature=0.7)
      state["results"]["final_plan"] = response
      return state

  async def __call__(self, state: AcademicState) -> Dict:
      """Execute the planning workflow"""
      # Ensure results dictionary exists
      if "results" not in state:
          state["results"] = {}
      print("-------- PlannerAgent --------")    
    #   try:
    #       display(Image(self.workflow.get_graph().draw_mermaid_png()))
    #   except Exception:
    #       pass

      # Run the graph
      final_state = await self.workflow.ainvoke(state)
    #   print("------------------------------")
      return {"plan": final_state["results"]["final_plan"]}