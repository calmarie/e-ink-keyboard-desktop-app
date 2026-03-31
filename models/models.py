import json
from dataclasses import dataclass, asdict, field

@dataclass
class KeyInfo:
    id: int
    action_type: str | None = None
    keys: list[str] = field(default_factory=list)
    image: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
