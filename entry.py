from concurrent.futures import ThreadPoolExecutor

from gesture_reciever_test import Keyboard
from sound_keyboard.face_gesture_detector.face_gesture_detector import FaceGestureDetector
from sound_keyboard.queue import (
    get_queue
)


def main():
    queue = get_queue()
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(Keyboard(queue).run())
        executor.submit(FaceGestureDetector(queue).run())


if __name__ == '__main__':
    main()
