import time

from sound_keyboard.face_gesture_detector.enums import (
    EyeDirection,
    EyeState,
    MouthState,
    Gestures
)

class Gesture_sender():
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        print("running gesture sender")
        while True:
            time.sleep(5)
            gestures = Gestures(
                eye_direction = EyeDirection.RIGHT,
                left_eye_state = EyeState.OPEN,
                right_eye_state = EyeState.OPEN,
                mouth_state = MouthState.CLOSE
            )
            self.queue.put((gestures, time.time()))