from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Dict

class TweakCategory(Enum):
    PERFORMANCE = auto()
    LATENCY = auto()
    NETWORK = auto()
    OTHER = auto()

@dataclass
class TweakDefinition:
    id: str
    name_ru: str
    category: TweakCategory
    apply_func: Optional[Callable[[bool], bool]] = None
    check_func: Optional[Callable[[], bool]] = None
    tooltip: str = ""
    
    # Optional fields for future use or registry mapping
    registry_path: Optional[str] = None
    default_value: Optional[object] = None
