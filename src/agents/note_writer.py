import json
from typing import Dict
from src.cors.models import AcademicState
from src.agents.react import ReActAgent

class NoteWriterAgent(ReActAgent):
  """
  Specialized agent for creating study notes using ReAct framework
  Focuses on creating concise, effective study materials based on learning style
  """

  def __init__(self, llm):
      """
      Initialize NoteWriterAgent with language model and example templates

      Args:
          llm: Language model instance for note generation
      """
      # Initialize parent ReActAgent
      super().__init__(llm)

      # Define few-shot examples for better note generation
      self.few_shot_examples = [
          {
              # Example of emergency study situation
              "input": "Need to cram Calculus III for tomorrow",
              "template": "Quick Review",
              "notes": """CALCULUS III ESSENTIALS:

              1. VECTORS & SURFACES
                 • Vectors = magnitude + direction
                 • Surfaces: level curves, gradients
                 • KEY FORMULAS:
                   - Dot product: a⋅b = |a||b|cosθ
                   - Cross product: |a×b| = |a||b|sinθ

              2. CRITICAL CONCEPTS (80% of exam)
                 • Partial derivatives → rate of change
                 • Multiple integrals → volume/area
                 • Vector fields → flow/force

              3. MUST-KNOW TRICKS
                 • Gradient = steepest increase
                 • Divergence = outward flux
                 • Curl = rotation measure

              4. COMMON EXAM PROBLEMS
                 • Find critical points
                 • Calculate flux/work
                 • Optimize with constraints

              EMERGENCY TIPS:
              • Draw pictures for vector problems
              • Check units match
              • When stuck: gradient → direction"""
          }
      ]

  async def __call__(self, state: AcademicState) -> Dict:
      """
      Generate study notes based on user's learning style and request

      Args:
          state (AcademicState): Current academic state including profile and messages

      Returns:
          Dict: Generated study notes
      """
      # Extract user profile and learning style preferences
      profile = state["profile"]
      learning_style = profile["learning_preferences"]["learning_style"]

      # Construct prompt for note generation
      prompt = f"""You're an expert at creating last-minute exam notes. Create concise, high-impact study materials.
      Pls act as an intelligent tool to help the students reach their goals or overcome struggles and answer with informal words.
      RULES:
      1. Focus on most tested concepts (80/20 rule)
      2. Include critical formulas and tricks
      3. Highlight common exam patterns
      4. Add emergency problem-solving tips
      5. Format for quick visual scanning
      6. Use {learning_style["primary"]} learning style techniques

      Context:
      - Learning Style: {json.dumps(learning_style, indent=2)}
      - Request: {state["messages"][-1].content}

      EXAMPLES:
      {json.dumps(self.few_shot_examples, indent=2)}

      Follow ReACT:
      1. Thought: [Analyze needs and search strategy]
      2. Action: [Use search_web/search_github]
      3. Observation: [Search findings]
      4. Notes: [Structured format]
        - Core Concepts (80/20)
        - Easy to remember but comprehensive
        - Key Formulas
        - Problem Patterns
        - **Emergency Tips"""

      # Generate notes using LLM
      response = await self.llm.agenerate([
          {"role": "system", "content": prompt},
          {"role": "user", "content": state["messages"][-1].content}
      ])

      # Return generated notes
      return {"notes": response}