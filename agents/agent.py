"""
Sri Lanka Travel Agent - Root Agent Definition for ADK
This file exports the root_agent for the ADK CLI to discover.
"""
from agents.workflow import root_agent

# ADK expects either 'root_agent' or 'agent' as the main entry point
agent = root_agent

__all__ = ['root_agent', 'agent']
