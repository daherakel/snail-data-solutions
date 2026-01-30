"""
Prompts System
Sistema modular de prompts para el módulo AWS Bedrock Agents
"""

from .base_prompts import BasePrompts
from .customer_support import CustomerSupportPrompts
from .document_assistant import DocumentAssistantPrompts

__all__ = [
    "BasePrompts",
    "DocumentAssistantPrompts",
    "CustomerSupportPrompts",
]
