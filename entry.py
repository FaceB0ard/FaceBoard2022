from concurrent.futures import ThreadPoolExecutor

from sound_keyboard.keyboard.keyboard import Keyboard
from sound_keyboard.face_gesture_detector.face_gesture_detector import FaceGestureDetector
from sound_keyboard.queue import get_queue

def main():
    queue = get_queue()

    with ThreadPoolExecutor() as executor:
        executor.submit(FaceGestureDetector(queue).run())
        # executor.submit(Keyboard(queue).run())

if __name__ == '__main__':
    main()