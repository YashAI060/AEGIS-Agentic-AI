from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RouterDecision:
    intent: str              # e.g., "WEB_SEARCH", "SYSTEM_CONTROL", "MEMORY_WRITE"
    route: str               # "REFLEX", "LOCAL_LLM", "CLOUD_LLM", "TOOL_CHAIN"
    confidence: float        # 0.0 to 1.0
    privacy_risk: bool       # True if sensitive data detected
    tools: List[str]         # e.g., ["weather_api", "gemini_summary"]
    requires_confirmation: bool = False
    clarification_needed: bool = False