import pygame

REPEAT_CYCLE = ("off", "all", "one")


def apply_key(key, player, playlist):
    if key in (pygame.K_ESCAPE, pygame.K_q):
        return "quit"
    if key == pygame.K_SPACE:
        player.toggle_pause()
        return "pause"
    if key == pygame.K_LEFT:
        player.seek(-5.0)
        return "seek"
    if key == pygame.K_RIGHT:
        player.seek(5.0)
        return "seek"
    if key == pygame.K_UP:
        player.set_volume(player.volume + 0.05)
        return "volume"
    if key == pygame.K_DOWN:
        player.set_volume(player.volume - 0.05)
        return "volume"
    if key == pygame.K_n:
        playlist.next()
        return "next"
    if key == pygame.K_p:
        playlist.prev()
        return "prev"
    if key == pygame.K_s:
        playlist.shuffle = not playlist.shuffle
        playlist._queue = []
        return "shuffle"
    if key == pygame.K_v:
        return "visualize"
    if key == pygame.K_r:
        index = (REPEAT_CYCLE.index(playlist.repeat) + 1) % len(REPEAT_CYCLE)
        playlist.repeat = REPEAT_CYCLE[index]
        return "repeat"
    return None
