"""Prompt management for Deep Agents.

This module provides centralized access to system prompts for all agents and subagents.
Prompts are organized by agent type to maintain clarity and ease of maintenance.
"""

from src.prompts.orchestrator import get_orchestrator_prompt
from src.prompts.component_analyzer import get_component_analyzer_prompt
from src.prompts.code_generator import get_code_generator_prompt

__all__ = [
    "get_orchestrator_prompt",
    "get_component_analyzer_prompt",
    "get_code_generator_prompt",
]
