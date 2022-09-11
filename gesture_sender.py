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
        pygame.display.set_caption("Gesture Sender")
        self.surface = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

    def draw(self):
        self.surface.fill((255, 255, 255))
        pygame.display.update()
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_RETURN:
                    print("Enter")
        pass

    def run(self):
        print("running gesture sender")
        while True:
            self.draw()
            self.update()

if __name__ == '__main__':
    queue = get_queue()
    Gesture_sender(queue).run()