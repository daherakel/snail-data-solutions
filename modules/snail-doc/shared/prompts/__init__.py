"""
Prompts System
Sistema modular de prompts para el módulo AWS Bedrock Agents
"""

from .base_prompts import BasePrompts
from .document_assistant import DocumentAssistantPrompts
from .customer_support import CustomerSupportPrompts

__all__ = [
    'BasePrompts',
    'DocumentAssistantPrompts',
    'CustomerSupportPrompts',
]

