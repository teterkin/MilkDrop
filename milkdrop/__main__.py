import argparse
from pathlib import Path

from milkdrop.app import MilkDropApp
from milkdrop.config import Config

CONFIG_PATH = Path.home() / ".config" / "milkdrop" / "config.json"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="milkdrop",
        description="Minimalist Winamp-style mp3 player with MilkDrop-like visuals.",
    )
    parser.add_argument("path", help="mp3 file or folder to play")
    parser.add_argument(
        "--fullscreen", action="store_true", help="start fullscreen"
    )
    args = parser.parse_args(argv)

    config = Config.load(CONFIG_PATH)
    if args.fullscreen:
        config.fullscreen = True

    app = MilkDropApp(args.path, config)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
