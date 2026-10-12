import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

_UNPERSISTED = frozenset({"fullscreen"})


@dataclass
class Config:
    volume: float = 0.8
    repeat: str = "off"
    shuffle: bool = False
    fullscreen: bool = False
    width: int = 960
    height: int = 540
    visualizer: str = "milkdrop"

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.is_file():
            return cls()
        data = json.loads(path.read_text())
        known = {field.name for field in fields(cls)}
        filtered = {
            key: value
            for key, value in data.items()
            if key in known and key not in _UNPERSISTED
        }
        return cls(**filtered)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            key: value
            for key, value in asdict(self).items()
            if key not in _UNPERSISTED
        }
        path.write_text(json.dumps(data, indent=2) + "\n")
