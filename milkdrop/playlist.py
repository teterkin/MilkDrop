import random
from pathlib import Path


class PlaylistError(Exception):
    pass


class Playlist:
    def __init__(self, tracks=None, repeat="off", shuffle=False, rng=None):
        self.tracks = list(tracks or [])
        self.repeat = repeat
        self.shuffle = shuffle
        self.rng = rng or random.Random()
        self.index = 0
        self._queue = []

    @property
    def current(self):
        if not self.tracks:
            return None
        return self.tracks[self.index]

    def _refill_queue(self):
        others = [i for i in range(len(self.tracks)) if i != self.index]
        self._queue = self.rng.sample(others, len(others))

    def _step(self, delta):
        if not self.tracks:
            return None
        if self.repeat == "one":
            return self.current
        new_index = self.index + delta
        if new_index < 0 or new_index >= len(self.tracks):
            if self.repeat == "all":
                new_index %= len(self.tracks)
            else:
                new_index = min(max(new_index, 0), len(self.tracks) - 1)
        self.index = new_index
        return self.current

    def next(self):
        if not self.tracks:
            return None
        if self.repeat == "one":
            return self.current
        if self.shuffle:
            if not self._queue:
                self._refill_queue()
            if not self._queue:
                return self.current
            self.index = self._queue.pop(0)
            return self.current
        return self._step(1)

    def prev(self):
        return self._step(-1)


def scan_folder(path):
    folder = Path(path)
    if folder.is_file():
        return [folder] if folder.suffix.lower() == ".mp3" else []
    try:
        entries = list(folder.iterdir())
    except OSError as exc:
        raise PlaylistError(
            f"cannot read folder '{folder}': {exc}. On macOS, grant your "
            "terminal Full Disk Access in System Settings > Privacy & Security "
            "> Full Disk Access (protected folders like ~/Music require it)."
        ) from exc
    files = [
        p
        for p in entries
        if p.is_file() and p.suffix.lower() == ".mp3"
    ]
    return sorted(files, key=lambda p: p.name.lower())
