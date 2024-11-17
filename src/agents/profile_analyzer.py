import json
from typing import Dict
from src.cors.models import AcademicState
from src.config import NeMoLLaMa
import os

async def profile_analyzer(state: AcademicState) -> Dict:
    """Analyze profile and extract relevant learning preferences"""
    profile = state["profile"]

    prompt = """Analyze student profile and extract key learning preferences:
    Profile: {profile}

    Focus on:
    - Learning style
    - ADHD patterns
    - Energy cycles
    - Environmental preferences
    - Motivation triggers
    - Distraction patterns
    - Optimal study times

    Return only the most relevant information for planning.
    """

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(profile)}
    ]

    llm = NeMoLLaMa(os.environ["NEMOTRON_4_340B_INSTRUCT_KEY"])
    response = await llm.agenerate(messages)
    state["results"]["profile_analysis"] = response
    return state