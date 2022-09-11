import time
from sound_keyboard.queue import get_queue
from sound_keyboard.face_gesture_detector.enums import (
    EyeDirection,
    EyeState,
    MouthState,
    Gestures
)
import pygame

class Gesture_sender:
    def __init__(self, queue):
        self.queue = queue
        pygame.init()
        pass

    def run(self):
        while True:
            pass