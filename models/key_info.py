import json
from dataclasses import dataclass, field


@dataclass
class KeyInfo:
    id: int
    img: list[int] = field(default_factory=list)
    action: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "img": self.img,
            "action": self.action,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_bytes(self) -> bytes:
        return f"{self.to_json()}\n".encode("utf-8")
    

