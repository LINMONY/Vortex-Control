from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Dict, Any, Tuple

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
    apply_func: Optional[Callable[[bool], Tuple[bool, str]]] = None
    check_func: Optional[Callable[[], bool]] = None
    tooltip: str = ""
    
    # Generic Registry Fields
    registry_path: Optional[str] = None
    value_name: Optional[str] = None
    value_on: Optional[Any] = None
    value_off: Optional[Any] = None
    value_type: str = "REG_DWORD"
    detailed_info: Optional[str] = None
    
    # Validation & Filtering
    hardware_tags: list[str] = field(default_factory=list) # e.g. ["NVIDIA", "AMD_GPU", "AMD_CPU", "INTEL_CPU"]
    
    # Optional fields for future use or registry mapping
    default_value: Optional[object] = None
