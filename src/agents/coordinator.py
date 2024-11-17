import json
from typing import Dict
from src.cors.models import AcademicState
from src.config import NeMoLLaMa
import os

async def analyze_context(state: AcademicState) -> Dict:
    """Analyze state context for coordinator decision making"""
    profile = state.get("profile", {})
    calendar = state.get("calendar", {})
    tasks = state.get("tasks", {})

    # Extract relevant course info
    courses = profile.get("academic_info", {}).get("current_courses", [])
    current_course = None
    request = state["messages"][-1].content.lower()

    for course in courses:
        if course["name"].lower() in request:
            current_course = course
            break

    return {
        "student": {
            "major": profile.get("personal_info", {}).get("major", "Unknown"),
            "year": profile.get("personal_info", {}).get("academic_year"),
            "learning_style": profile.get("learning_preferences", {}).get("learning_style", {}),
        },
        "course": current_course,
        "upcoming_events": len(calendar.get("events", [])),
        "active_tasks": len(tasks.get("tasks", [])),
        "study_patterns": profile.get("learning_preferences", {}).get("study_patterns", {})
    }

def parse_coordinator_response(response: str) -> Dict:
    """Parse LLM response into coordinator analysis"""
    try:
        # Default analysis
        analysis = {
            "required_agents": ["PLANNER"],
            "priority": {"PLANNER": 1},
            "concurrent_groups": [["PLANNER"]],
            "reasoning": "Default coordination"
        }

        # Parse response for ReACT patterns
        if "Thought:" in response and "Decision:" in response:
            # Extract decisions about agents
            if "NoteWriter" in response or "note" in response.lower():
                analysis["required_agents"].append("NOTEWRITER")
                analysis["priority"]["NOTEWRITER"] = 2
                analysis["concurrent_groups"] = [["PLANNER", "NOTEWRITER"]]

            if "Advisor" in response or "guidance" in response.lower():
                analysis["required_agents"].append("ADVISOR")
                analysis["priority"]["ADVISOR"] = 3

            # Extract reasoning if present
            thought_section = response.split("Thought:")[1].split("Action:")[0].strip()
            analysis["reasoning"] = thought_section

        return analysis

    except Exception as e:
        print(f"Parse error: {str(e)}")
        return {
            "required_agents": ["PLANNER"],
            "priority": {"PLANNER": 1},
            "concurrent_groups": [["PLANNER"]],
            "reasoning": "Fallback due to parse error"
        }

async def coordinator_agent(state: AcademicState) -> Dict:
    try:
        context = await analyze_context(state)
        query = state["messages"][-1].content

        prompt = """You are a coordinator using ReACT framework. Analyze query, deploy minimal required agents, verify results.

        SEMANTIC ACTIONS:
        1. Understand schedule & constraints
        2. Extract key user info/needs
        3. Determine focus areas
        4. Select minimal required agents
        5. Verify agent outputs

        FORMAT:
        Thought: [Analyze query and context]
        Action: [Select initial agent]
        Observation: [Review agent output]
        Decision: [Complete/Need next agent]

        Current request: {request}
        Context: {context}
        """

        def parse_result(output: str) -> Dict:
            try:
                if "need next agent" in output.lower():
                    # Extract next agent from decision
                    next_agent = ["NOTEWRITER"] if "note" in output.lower() else ["ADVISOR"]
                    return {
                        "required_agents": ["PLANNER", next_agent[0]],
                        "priority": {"PLANNER": 1, next_agent[0]: 2},
                        "concurrent_groups": [["PLANNER"], next_agent],
                        "reasoning": output
                    }
                else:
                    return {
                        "required_agents": ["PLANNER"],
                        "priority": {"PLANNER": 1},
                        "concurrent_groups": [["PLANNER"], next_agent],
                        "reasoning": output
                    }
            except Exception as e:
                print(e)
                return {"required_agents": ["PLANNER"]}

        llm = NeMoLLaMa(os.environ["NEMOTRON_4_340B_INSTRUCT_KEY"])
        response = await llm.agenerate([
            {"role": "system", "content": prompt.format(
                request=query,
                context=json.dumps(context, indent=2)
            )}
        ])

        return {
            "results": {
                "coordinator_analysis": parse_result(response)
            }
        }
    except Exception as e:
        return {"results": {"coordinator_analysis": {"required_agents": ["PLANNER"]}}}