from dataclasses import dataclass, asdict, field

@dataclass
class KeyInfo:
    id: int
    action_type: str | None = None
    keys: list[str] = field(default_factory=list)
    image: str=""
