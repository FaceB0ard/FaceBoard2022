from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from sound_keyboard.keyboard.keyboard import Keyboard
from sound_keyboard.face_gesture_detector.face_gesture_detector import FaceGestureDetector
from sound_keyboard.queue import get_queue


def main():
    queue = get_queue()

    Thread(target = lambda : Keyboard(queue).run()).start()
    Thread(target = lambda : FaceGestureDetector(queue).run()).start()

    """with ThreadPoolExecutor() as executor:
        executor.submit(lambda: FaceGestureDetector(queue).run())
        executor.submit(Keyboard(queue).run())"""


if __name__ == '__main__':
    main()
