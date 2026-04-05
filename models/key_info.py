import json
from dataclasses import asdict, dataclass, field


@dataclass
class KeyInfo:
    id: int
    action_type: str | None = None
    keys: list[str] = field(default_factory=list)
    image: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
