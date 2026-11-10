import tkinter as tk
import random
import threading
import math

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

def play_sfx(effect):
    if not HAS_SOUND: return
    def _play():
        try:
            if effect == 'intro':
                for f in [261, 329, 392, 523, 659]: winsound.Beep(f, 100)
            elif effect == 'bounce': winsound.Beep(600, 40)
            elif effect == 'hit': winsound.Beep(1200, 30)
            elif effect == 'break': winsound.Beep(1600, 50)
            elif effect == 'powerup':
                winsound.Beep(800, 80)
                winsound.Beep(1600, 100)
            elif effect == 'shoot': winsound.Beep(2000, 20)
            elif effect == 'explosion': winsound.Beep(100, 150)
            elif effect == 'bad': winsound.Beep(200, 150)
            elif effect == 'levelup':
                for f in [523, 659, 783, 1046]: winsound.Beep(f, 120)
            elif effect == 'lose':
                for f in [300, 250, 200]: winsound.Beep(f, 300)
        except: pass
    threading.Thread(target=_play, daemon=True).start()
