from threading import Thread

from gesture_reciever_test import Keyboard
#from gesture_sender import Gesture_sender
from gesture_sender_simple import Gesture_sender
from sound_keyboard.queue import (
    get_queue
)

def main():
    queue = get_queue()
    Thread(target = lambda : Keyboard(queue).run()).start()
    Thread(target = lambda : Gesture_sender(queue).run()).start()

if __name__ == '__main__':
    main()