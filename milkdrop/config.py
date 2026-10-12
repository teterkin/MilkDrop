import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path


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
        filtered = {key: value for key, value in data.items() if key in known}
        return cls(**filtered)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")
