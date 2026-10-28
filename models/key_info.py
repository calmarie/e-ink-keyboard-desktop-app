import json
from dataclasses import dataclass, field


USB_HID_USAGE_IDS = {
    "CTRL": 0x80,
    "CONTROL": 0x80,
    "LCTRL": 0x80,
    "LEFTCTRL": 0x80,
    "SHIFT": 0x81,
    "LSHIFT": 0x81,
    "LEFTSHIFT": 0x81,
    "ALT": 0x82,
    "LALT": 0x82,
    "LEFTALT": 0x82,
    "WIN": 0x83,
    "GUI": 0x83,
    "META": 0x83,
    "SUPER": 0x83,
    "COMMAND": 0x83,
    "CMD": 0x83,
    "RCTRL": 0x84,
    "RIGHTCTRL": 0x84,
    "RSHIFT": 0x85,
    "RIGHTSHIFT": 0x85,
    "RALT": 0x86,
    "RIGHTALT": 0x86,
    "RWIN": 0x87,
    "RIGHTGUI": 0x87,
    "ENTER": 0xB0,
    "RETURN": 0xB0,
    "ESC": 0xB1,
    "ESCAPE": 0xB1,
    "BACKSPACE": 0xB2,
    "TAB": 0xB3,
    "SPACE": 0x20,
    "SPACEBAR": 0x20,
    "MINUS": 0x2D,
    "-": 0x2D,
    "EQUAL": 0x3D,
    "=": 0x3D,
    "LEFTBRACKET": 0x5B,
    "[": 0x5B,
    "RIGHTBRACKET": 0x5D,
    "]": 0x5D,
    "BACKSLASH": 0x5C,
    "\\": 0x5C,
    "SEMICOLON": 0x3B,
    ";": 0x3B,
    "APOSTROPHE": 0x27,
    "'": 0x27,
    "QUOTE": 0x27,
    "GRAVE": 0x60,
    "`": 0x60,
    "TILDE": 0x60,
    "COMMA": 0x2C,
    ",": 0x2C,
    "PERIOD": 0x2E,
    ".": 0x2E,
    "DOT": 0x2E,
    "SLASH": 0x2F,
    "/": 0x2F,
    "CAPSLOCK": 0xC1,
    "PRINTSCREEN": 0xCE,
    "SCROLLLOCK": 0xCF,
    "PAUSE": 0xD0,
    "INSERT": 0xD1,
    "HOME": 0xD2,
    "PAGEUP": 0xD3,
    "DELETE": 0xD4,
    "DEL": 0xD4,
    "END": 0xD5,
    "PAGEDOWN": 0xD6,
    "RIGHT": 0xD7,
    "LEFT": 0xD8,
    "DOWN": 0xD9,
    "UP": 0xDA,
    "LEFTARROW": 0xD8,
    "RIGHTARROW": 0xD7,
    "UPARROW": 0xDA,
    "DOWNARROW": 0xD9,
}

for digit in "0123456789":
    USB_HID_USAGE_IDS[digit] = ord(digit)

for offset in range(1, 13):
    USB_HID_USAGE_IDS[f"F{offset}"] = 0xC1 + offset

for offset in range(13, 25):
    USB_HID_USAGE_IDS[f"F{offset}"] = 0xF0 + offset - 13


def encode_hotkey(keys: list[str]) -> list[int]:
    encoded_keys: list[int] = []

    for raw_key in keys:
        stripped_key = raw_key.strip().replace(" ", "")
        normalized_key = stripped_key.upper()

        if len(stripped_key) == 1 and stripped_key.isalpha():
            usage_id = ord(stripped_key.lower())
        else:
            usage_id = USB_HID_USAGE_IDS.get(normalized_key)
        if usage_id is None:
            raise ValueError(f"Неизвестная клавиша для USB HID: {raw_key}")
        encoded_keys.append(usage_id)

    return encoded_keys


@dataclass
class KeyInfo:
    id: int
    img: list[int] = field(default_factory=list)
    action: list[int] | str = field(default_factory=list)

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
    

