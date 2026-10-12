import pygame

from milkdrop.analysis import BeatDetector, SpectrumAnalyzer
from milkdrop.audio import AudioPlayer
from milkdrop.controls import apply_key
from milkdrop.playlist import Playlist, scan_folder
from milkdrop.timefmt import format_time
from milkdrop.visualizer.render import Visualizer

SAMPLE_RATE = 44100
INTERNAL_WIDTH = 480
INTERNAL_HEIGHT = 270


class MilkDropApp:
    def __init__(self, start_path, config):
        self.config = config

        tracks = scan_folder(start_path)

        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)

        flags = pygame.FULLSCREEN if config.fullscreen else 0
        self.screen = pygame.display.set_mode((config.width, config.height), flags)
        pygame.display.set_caption("MilkDrop")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.playlist = Playlist(
            tracks, repeat=config.repeat, shuffle=config.shuffle
        )
        self.player = AudioPlayer(pygame.mixer.music, sample_rate=SAMPLE_RATE)
        self.analyzer = SpectrumAnalyzer(SAMPLE_RATE, num_bands=64, smoothing=0.6)
        self.beat = BeatDetector()
        self.visualizer = Visualizer(
            INTERNAL_WIDTH, INTERNAL_HEIGHT, num_bands=64
        )

        self.running = False
        self._load_current()

    def _load_current(self):
        if not self.playlist.current:
            return
        self.player.load(self.playlist.current)
        self.player.set_volume(self.config.volume)
        self.player.play()

    def _advance(self):
        self.playlist.next()
        self._load_current()

    def compute_frame(self):
        window = self.player.analysis_window(self.analyzer.fft_size)
        bands = self.analyzer.analyze(window)
        low_count = max(1, len(bands) // 8)
        low_energy = float(bands[:low_count].mean()) if len(bands) else 0.0
        beat = self.beat.update(low_energy)
        return self.visualizer.render(bands, beat)

    def _handle_action(self, action):
        if action == "quit":
            self.running = False
        elif action in ("next", "prev"):
            self._load_current()

    def _blit_frame(self, frame):
        surface = pygame.surfarray.make_surface(
            frame.swapaxes(0, 1).copy()
        )
        scaled = pygame.transform.smoothscale(surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))

    def _draw_hud(self):
        duration = (
            len(self.player.samples) / self.player.sample_rate
            if self.player.samples is not None
            else 0.0
        )
        track = self.playlist.current
        name = track.name if track else "-"
        status = "paused" if self.player.paused else "playing"
        line = (
            f"{name}  {format_time(self.player.position())}/{format_time(duration)}"
            f"  vol {int(self.player.volume * 100)}%"
            f"  repeat:{self.playlist.repeat}"
            f"  {'shuffle ' if self.playlist.shuffle else ''}{status}"
        )
        label = self.font.render(line, True, (235, 235, 235))
        self.screen.blit(label, (10, 10))

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    action = apply_key(event.key, self.player, self.playlist)
                    self._handle_action(action)

            self._blit_frame(self.compute_frame())
            self._draw_hud()
            pygame.display.flip()
            self.clock.tick(60)

            if (
                self.player.samples is not None
                and not self.player.paused
                and not pygame.mixer.music.get_busy()
            ):
                self._advance()

        pygame.quit()
