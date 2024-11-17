from langgraph.graph import StateGraph, END, START
from src.cors.models import AcademicState
from src.agents.coordinator import coordinator_agent
from src.agents.profile_analyzer import profile_analyzer
from src.agents.executor import AgentExecutor

def create_agents_graph(llm) -> StateGraph:
    workflow = StateGraph(AcademicState)
    executor = AgentExecutor(llm)

    # Add nodes
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("profile_analyzer", profile_analyzer)
    workflow.add_node("execute", executor.execute)

    # Add edges
    workflow.add_edge(START, "coordinator")
    workflow.add_edge("coordinator", "profile_analyzer")
    workflow.add_edge("profile_analyzer", "execute")

    def should_end(state):
        # Check if all required agents have run
        analysis = state["results"].get("coordinator_analysis", {})
        executed_agents = set(state["results"].get("agent_outputs", {}).keys())
        required_agents = set(a.lower() for a in analysis.get("required_agents", []))

        # End if all required agents have executed
        if required_agents.issubset(executed_agents):
            return END
        return "coordinator"

    workflow.add_conditional_edges("execute", should_end, {"coordinator": "coordinator", END: END})

    return workflow.compile()