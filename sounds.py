from pygame import mixer
from pathlib import Path

mixer.pre_init(44100, -16, 2, 512)
mixer.init(44100, -16, 2, 512)

sounds_channel = mixer.Channel(1)

class Sounds:
    def __init__(self):
        self.waka = mixer.Sound(Path("Resources") / "sounds" / "pac-man-waka-waka.mp3")
        self.die = mixer.Sound(Path("Resources") / "sounds" / "pacman-die.mp3")
        self.glup = mixer.Sound(Path("Resources") / "sounds" / "sor-pacman.mp3")
        self.start = mixer.Sound(Path("Resources") / "sounds" / "start-pacman.mp3")
        self.win = mixer.Sound(Path("Resources") / "sounds" / "followw.mp3")
        
        sounds_channel.set_volume(0.67)
    

    def play_sound(self, sound):
        if not sounds_channel.get_busy():
            match sound:
                case "waka": sounds_channel.play(self.waka)
                case "die": sounds_channel.play(self.die)
                case "glup": sounds_channel.play(self.glup)
                case "start": sounds_channel.play(self.start)
                case "win": sounds_channel.play(self.win)

    def stop_sound(self):
        mixer.stop()