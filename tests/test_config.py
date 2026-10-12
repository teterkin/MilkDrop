from milkdrop.config import Config


def test_defaults():
    cfg = Config()

    assert cfg.volume == 0.8
    assert cfg.repeat == "off"
    assert cfg.shuffle is False
    assert cfg.fullscreen is False
    assert (cfg.width, cfg.height) == (960, 540)


def test_load_missing_file_returns_defaults(tmp_path):
    cfg = Config.load(tmp_path / "nope.json")

    assert cfg.volume == 0.8
    assert cfg.repeat == "off"


def test_load_partial_overrides_and_ignores_unknown_keys(tmp_path):
    path = tmp_path / "c.json"
    path.write_text('{"volume": 0.3, "bogus": 1}')

    cfg = Config.load(path)

    assert cfg.volume == 0.3
    assert cfg.repeat == "off"
    assert not hasattr(cfg, "bogus")


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "c.json"
    original = Config(volume=0.25, repeat="all", shuffle=True, width=1280, height=720)

    original.save(path)
    reloaded = Config.load(path)

    assert reloaded == original

