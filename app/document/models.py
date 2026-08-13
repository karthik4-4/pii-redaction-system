from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class RunSpan:
    run_index: int
    start_char: int
    end_char: int
    text: str
    run_obj: Any

@dataclass
class TextBlock:
    block_id: str
    block_type: str  # 'paragraph', 'cell', 'header', 'footer'
    text: str
    runs: List[RunSpan] = field(default_factory=list)
    raw_element: Any = None
    section_index: int = 0
    row_index: Optional[int] = None
    col_index: Optional[int] = None

@dataclass
class PIIEntity:
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DetectionResult:
    block_id: str
    entities: List[PIIEntity] = field(default_factory=list)

@dataclass
class ReplacementMapping:
    entity_type: str
    original_text: str
    synthetic_value: str
