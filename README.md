# MilkDrop

Минималистичный музыкальный плеер в духе Winamp: проигрывает **mp3** и рисует
аудиореактивную визуализацию **в стиле MilkDrop** (feedback-буфер, варп,
спектр, пульс на бит).

## Возможности

- Проигрывание mp3 (через `pygame.mixer`, SDL_mixer).
- Плейлист из папки: `n` / `p` — следующий / предыдущий трек.
- Режимы повтора (`off` → `all` → `one`) и перемешивание.
- Полноэкранная MilkDrop-подобная визуализация: предыдущий кадр затухает,
  масштабируется и поворачивается, поверх — спектр из 64 полос; сильная доля
  даёт импульс.
- HUD: имя трека, время, громкость, режим.
- Управление с клавиатуры, настройки в `~/.config/milkdrop/config.json`.

## Требования

- Python 3.12
- `ffmpeg` в `PATH` (используется для декодирования mp3 в PCM)
- macOS (проверено); на Linux/Windows — best-effort

## Установка

```sh
python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt
# либо: .venv/bin/pip install -r requirements-dev.txt
```

Зависимости закреплены точно: `pygame==2.6.1`, `numpy==2.5.4`, `pytest==9.1.1`.

## Запуск

```sh
.venv/bin/python -m milkdrop /path/to/song.mp3
.venv/bin/python -m milkdrop /path/to/music_folder   # вся папка как плейлист
.venv/bin/python -m milkdrop --fullscreen song.mp3
```

## Управление

| Клавиша     | Действие                          |
|-------------|-----------------------------------|
| `Space`     | пауза / продолжить                |
| `←` / `→`   | перемотка на -5с / +5с            |
| `↑` / `↓`   | громкость +5% / -5%               |
| `n` / `p`   | следующий / предыдущий трек       |
| `r`         | режим повтора: off → all → one    |
| `s`         | вкл/выкл перемешивание            |
| `q` / `Esc` | выход                             |

## Архитектура

```
milkdrop/
  __main__.py        CLI-точка входа
  app.py             окно, игровой цикл, HUD (pygame)
  controls.py        маппинг клавиш -> действия (чистая логика)
  audio.py           ffmpeg -> PCM -> numpy, play/seek/позиция
  analysis.py        FFT -> 64 лог-полосы, детектор бита
  playlist.py        скан папки, next/prev/shuffle/repeat
  config.py          настройки (JSON, дефолты)
  timefmt.py         формат времени
  visualizer/render.py  feedback-варп, затухание, спектр
```

Визуализация рендерится во внутреннем разрешении 480×270 и апскейлится на окно
(замер: ~72 fps на M-series).

## Тесты

```sh
.venv/bin/python -m pytest
```

32 теста: разбор сигнала, плейлист, конфиг, чистые хелперы аудио, примитивы
рендера, управление, CLI и headless-прогон цикла приложения
(`SDL_VIDEODRIVER=dummy`).

## Время

См. [`docs/TIMING.md`](docs/TIMING.md).

## Лицензия

MIT.
