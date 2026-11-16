"""Procedural audio and shared neon block rendering; no asset downloads."""
from array import array
import math
import pygame


class Sounds:
    def __init__(self):
        self.muted = False
        self.clips = {}
        self.error = None
        self.music = None
        self.music_channel = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            rate, sample_format, channels = pygame.mixer.get_init()
            if sample_format != -16:
                self.error = "Unsupported audio format"
                return
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(1)
            self.music_channel = pygame.mixer.Channel(0)
            melodies = {
                "start": [(523, .13), (659, .13), (784, .13), (1047, .25)],
                "move": [(440, .045)],
                "drop": [(440, .045), (220, .06), (110, .12)],
                "rotate": [(660, .055), (880, .065)],
                "hold": [(440, .07), (660, .09)],
                "lock": [(150, .08), (100, .06)],
                "clear": [(523, .09), (659, .09), (784, .09), (1047, .16)],
                "over": [(392, .16), (330, .16), (262, .16), (196, .32)],
                "pause": [(440, .06), (330, .08)],
            }
            for name, notes in melodies.items():
                samples = array('h')
                for frequency, duration in notes:
                    count = int(rate * duration)
                    for index in range(count):
                        envelope = min(1, index / (rate * .006)) * (1 - index / count) ** 2
                        phase = 2 * math.pi * frequency * index / rate
                        value = int(16000 * envelope * (math.sin(phase) + .2 * math.sin(2 * phase)))
                        samples.extend([value] * channels)
                self.clips[name] = pygame.mixer.Sound(buffer=samples.tobytes())
            # Original looping synth melody with a quiet bass accompaniment.
            samples = array('h')
            melody = [64, 67, 71, 67, 62, 66, 69, 66,
                      60, 64, 67, 64, 62, 66, 69, 71,
                      64, 71, 76, 71, 62, 69, 74, 69,
                      60, 67, 72, 67, 62, 66, 69, 66]
            count = int(rate * .24)
            for step, note in enumerate(melody):
                frequency = 440 * 2 ** ((note - 69) / 12)
                bass = 440 * 2 ** (([40, 38, 36, 38][step // 4 % 4] - 69) / 12)
                for index in range(count):
                    t = index / rate
                    envelope = min(1, t / .008) * min(1, (count-index) / (rate*.035))
                    value = int(envelope * (4200 * math.sin(2*math.pi*frequency*t)
                                           + 2200 * math.sin(2*math.pi*bass*t)))
                    samples.extend([value] * channels)
            self.music = pygame.mixer.Sound(buffer=samples.tobytes())
            self.music_channel.set_volume(.5)
            self.music_channel.play(self.music, loops=-1)
            self.play("start")
        except pygame.error as error:
            self.error = str(error)
            print("Audio initialization failed:", self.error)

    def play(self, name):
        if not self.muted and name in self.clips:
            channel = pygame.mixer.find_channel(force=True)
            if channel:
                channel.set_volume(1)
                channel.play(self.clips[name])

    def toggle(self):
        self.muted = not self.muted
        if self.muted and pygame.mixer.get_init():
            pygame.mixer.stop()
        elif self.music_channel and self.music:
            self.music_channel.play(self.music, loops=-1)
            self.play("start")

    def set_paused(self, paused):
        if self.music_channel:
            if paused:
                self.music_channel.pause()
            elif not self.muted:
                self.music_channel.unpause()


def draw_block(screen, rect, color):
    rect = pygame.Rect(rect)
    dark = tuple(int(c * .45) for c in color)
    light = tuple(min(255, int(c * .65 + 90)) for c in color)
    pygame.draw.rect(screen, dark, rect, border_radius=5)
    pygame.draw.rect(screen, color, rect.inflate(-2, -3).move(0, -1), border_radius=4)
    pygame.draw.line(screen, light, (rect.left + 5, rect.top + 3),
                     (rect.right - 6, rect.top + 3), 2)
