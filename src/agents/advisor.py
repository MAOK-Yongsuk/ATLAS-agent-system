import json
from typing import Dict
from src.agents.react import ReActAgent
from src.cors.models import AcademicState

class AdvisorAgent(ReActAgent):
  """
  Academic advisor agent that provides personalized learning recommendations
  Uses ReAct framework to analyze student needs and provide targeted advice
  """

  def __init__(self, llm):
      """
      Initialize AdvisorAgent with language model and example scenarios

      Args:
          llm: Language model instance for generating advice
      """
      # Initialize parent ReActAgent
      super().__init__(llm)

      # Define few-shot examples for better advice generation
      self.few_shot_examples = [
          {
              # Example case for ADHD student support
              "request": "Struggling with ADHD and exam preparation - need help focusing and managing time",
              "profile": {
                  "performance": {"current_grade": "C", "areas_of_improvement": ["focus", "time_management"]},
                  "learning_style": "visual",
                  "adhd_support": {
                      "chunked_subtasks": True,
                      "timer_preferences": "25min work/5min break"
                  }
              },
              "thought": "Student needs structured approach with ADHD accommodations",
              "action": "check_learning_style",
              "observation": "Visual learner with ADHD-friendly task chunking needs",
              "advice": """Focus Strategy:
                  1. Break study sessions into 25-minute blocks
                  2. Use visual mind maps for quick concept review
                  3. Set specific mini-goals for each session
                  4. Implement physical movement breaks
                  5. Use timer for task transitions"""
          }
      ]

  async def __call__(self, state: AcademicState) -> Dict:
      """
      Generate personalized academic advice based on student profile and needs

      Args:
          state (AcademicState): Current academic state including profile and messages

      Returns:
          Dict: Structured advice and metadata
      """
      # Extract relevant information from profile
      profile = state["profile"]
      courses = profile.get("academic_info", {}).get("current_courses", [])
      learning_prefs = profile.get("learning_preferences", {})

      # Construct detailed system prompt for advice generation
      system_prompt = f"""You are an expert academic advisor using ReACT framework.

      Context:
      - Courses: {json.dumps(courses, indent=2)}
      - Learning Style: {json.dumps(learning_prefs.get("learning_style", {}), indent=2)}
      - Study Patterns: {json.dumps(learning_prefs.get("study_patterns", {}), indent=2)}

      Few-shot examples:
      {json.dumps(self.few_shot_examples, indent=2)}

      Steps:
      1. Analyze request and profile
      2. Use tools to gather information
      3. Provide targeted advice based on learning style and course needs
      4. Include specific tools and techniques

      Format:
      Thought: [Your analysis]
      Action: [Tool/check to perform]
      Observation: [What you found]
      Advice: [Your structured recommendations]

      Please act as a helpful kind friendly academic advisor
      """

      try:
          # Generate personalized advice using LLM
          response = await self.llm.agenerate([
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": state["messages"][-1].content}
          ])

          # Return structured response with metadata
          return {
              "advisor_output": {
                  "guidance": response,
                  "metadata": {
                      "course_specific": True,
                      "considers_learning_style": True
                  }
              }
          }
      except Exception as e:
          # Error handling with fallback advice
          print(f"Advisor error: {str(e)}")
          return {"advisor_output": {"guidance": "Focus on core concepts and practice regularly."}}

  async def check_performance(self, course_id: str, profile: Dict) -> Dict:
      """
      Analyze performance in specific course

      Args:
          course_id (str): Identifier for the course
          profile (Dict): Student profile containing academic information

      Returns:
          Dict: Course performance data
      """
      # Extract course information from profile
      courses = profile.get("academic_info", {}).get("current_courses", [])
      # Find specific course by ID
      course = next((c for c in courses if c["code"] == course_id), None)
      # Return performance data or empty dict if course not found
      return course.get("performance", {}) if course else {}