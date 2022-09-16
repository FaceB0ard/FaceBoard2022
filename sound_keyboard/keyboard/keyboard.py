import pygame
import sys
import time
from datetime import datetime
from utils import (
    convert_eye_direction_to_direction
)
from sound_keyboard.queue import (
    get_queue
)
from sound_keyboard.keyboard.state_controller import (
    KEYMAP,
    KeyboardStateController,
    Direction
)
from sound_keyboard.sound.sound import (
    read_aloud
)

from sound_keyboard.keyboard.add_template import (
    add_template
)

from sound_keyboard.face_gesture_detector.enums import (
    EyeDirection,
    EyeState,
    MouthState,
    Gestures
)

# constants
BACKGROUND_COLOR = (242, 242, 242)
KEYTILE_COLOR = (242, 242, 242)
# KEYTILE_COLOR = (255, 255, 255)
OVERLAY_COLOR = (0, 0, 0, 180)
FONT_COLOR = (12, 9, 10)
MAX_DELAY = 0.7

FONT_PATH = 'fonts/Noto_Sans_JP/NotoSansJP-Regular.otf'

class Keyboard:
    def __init__(self, queue):

        self.queue = queue
        # initialize app
        pygame.init()
        pygame.display.set_caption('FaceBoard')

        # setting initial window size and set window resizable
        self.surface = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)

        # setting keyboard controller
        self.keyboard_state_controller = KeyboardStateController()

        # state
        self.previous_gestures = None
        self.delay = 0
        self.detect_eye_status = None

        self.add_template_time = None
        self.move_to_left = None
        self.move_to_right = None
    
    def draw_text(self, char_info):
        char, pos, size = char_info

        font = pygame.font.Font(FONT_PATH, size)
        text = font.render(char, True, FONT_COLOR, None)
        textRect = text.get_rect()
        textRect.center = pos
        self.surface.blit(text, textRect)

    def draw_tile(self, char, center, radius, tile_color, border_size, font_size = 15):
        pygame.draw.circle(self.surface, tile_color, center, radius, border_size)
        self.draw_text((char, center, font_size))

    def draw_keyboard(self):
        kind = self.keyboard_state_controller.kind
        keymap = KEYMAP[kind]['parent'][0]

        width = self.surface.get_width()
        height = self.surface.get_height()

        base = width // 2

        # 真ん中、真ん中の隣、両端のサイズ
        cell_sizes = [100, 50, 20]
        font_sizes = [100, 50, 20]
        distances = [0, base // 2, base * 4 // 5]


        padding = 5

        center_index = keymap.index(self.keyboard_state_controller.current_parent_char)

        for dir in range(-2, 3):
            index = center_index + dir
            cell_size = cell_sizes[abs(dir)]
            font_size = font_sizes[abs(dir)]
            distance = distances[abs(dir)]

            sign = 1 if dir > 0 else -1

            if 0 <= index < len(keymap):
                self.draw_tile(
                    keymap[index],# if abs(dir) != 2 else '...',
                    (width // 2 +  sign * distance, height // 2),
                    cell_size,
                    KEYTILE_COLOR,
                    0,
                    font_size
                )
        
        # draw currently selected text 決定された文字の表示
        # 中央上部に表示
        self.draw_text((self.keyboard_state_controller.text, (width / 2, height * 7 // 8), 30))
        
        for i, text in enumerate(keymap):
            if keymap[i] == keymap[center_index]:
                self.draw_text((text, (self.surface.get_width() // 2 - len(keymap) // 2 * 30 + i*30 + 10, height // 8 - 20), 30))
            else:
                text = pygame.font.Font(FONT_PATH, 20).render(f'{text}', True, (127, 127, 127))
                self.surface.blit(text, (self.surface.get_width() // 2 - len(keymap) // 2 * 30 + i*30, height // 8 - 30))

    def updateKeyboardState(self, gestures: Gestures):
        # Gesturesオブジェクトの状態を読み出して操作を確定する
        if  gestures.eye_direction != EyeDirection.CENTER:
            direction = convert_eye_direction_to_direction(gestures.eye_direction)
            self.keyboard_state_controller.move(direction)
            if direction == Direction.LEFT:
                self.move_to_left = time.time()
            elif direction == Direction.RIGHT:
                self.move_to_right = time.time()
            return True
        
        # 正面で目を閉じたとき
        if (self.previous_gestures is None or self.previous_gestures.right_eye_state == EyeState.OPEN) and gestures.right_eye_state == EyeState.CLOSE and gestures.eye_direction == EyeDirection.CENTER:
            # まばたき判断システム
            self.detect_eye_status = []
            self.detect_eye_status.append(time.time())
            print('close eye')

        # 目を開けたとき
        if self.detect_eye_status is not None and self.previous_gestures.right_eye_state == EyeState.CLOSE and gestures.right_eye_state == EyeState.OPEN:
            self.detect_eye_status.append(time.time())
            print(f'open eye, diff: {self.detect_eye_status[1] - self.detect_eye_status[0]}')

            if len(self.detect_eye_status) == 2:
                if 0.2 < (self.detect_eye_status[1] - self.detect_eye_status[0]) < 1.0:
                    # 定を入力できないようにする
                    kind = self.keyboard_state_controller.kind
                    keymap = KEYMAP[kind]['children'][self.keyboard_state_controller.current_parent_char]
                    center_index = keymap.index(self.keyboard_state_controller.current_child_char)
                    if not (self.keyboard_state_controller.selected_parent and keymap[center_index] == "定"):
                        self.keyboard_state_controller.select()
                        self.detect_eye_status = None
                        return True
                elif 1.0 <= (self.detect_eye_status[1] - self.detect_eye_status[0]) < 5.0:
                    self.keyboard_state_controller.back()
                else:
                    self.detect_eye_status = None
        
        if (self.previous_gestures is None or self.previous_gestures.mouth_state == MouthState.CLOSE) and gestures.mouth_state == MouthState.OPEN:
            if self.keyboard_state_controller.text != "":
                read_aloud(self.keyboard_state_controller.text)
            self.keyboard_state_controller.clear()
            return True
        
        return False
    
    def draw_child_keyboard(self):
        kind = self.keyboard_state_controller.kind
        keymap = KEYMAP[kind]['children'][self.keyboard_state_controller.current_parent_char]
        width = self.surface.get_width()
        height = self.surface.get_height()

        base = width // 2

        cell_sizes = [100, 50, 20]
        font_sizes = [100, 50, 20]
        distances = [0, base // 2, base * 4 // 5]

        center_index = keymap.index(self.keyboard_state_controller.current_child_char)

        # draw currently selected text
        self.draw_text((self.keyboard_state_controller.text, (width / 2, height * 7 // 8), 30))

        # 描画順を変えてみる
        for dir in [-2, 2, -1, 1, 0]:
            index = center_index + dir
            cell_size = cell_sizes[abs(dir)]
            font_size = font_sizes[abs(dir)]
            distance = distances[abs(dir)]

            sign = 1 if dir > 0 else -1

            if 0 <= index < len(keymap):
                # 中央のみ表示をずらす
                if dir == 0:
                    self.draw_tile(
                        keymap[index],
                        (width // 2, height // 2),
                        cell_size,
                        KEYTILE_COLOR,
                        0,
                        font_size
                    )
                else:
                    self.draw_tile(
                        keymap[index], # if abs(dir) != 2 else '...',
                        (width // 2 +  sign * distance, height // 3),
                        cell_size,
                        KEYTILE_COLOR,
                        0,
                        font_size
                    )
    
    def draw_camera_status(self):
        # queueの中身がからでなければ、右上に緑丸を表示する
        if self.previous_gestures is not None:
            pygame.draw.circle(self.surface, (0, 220, 84), (self.surface.get_width() - 15, 15), 8, 0)
    
    def draw_triangle_gaze(self):
        if self.move_to_left:
            if time.time() - self.move_to_left > 0.1:
                text = pygame.font.Font(FONT_PATH, 30).render(f'◀', True, (0, 0, 0))
                self.surface.blit(text, (20, self.surface.get_height() // 2 - 20))
        else:
            text = pygame.font.Font(FONT_PATH, 30).render(f'◀', True, (0, 0, 0))
            self.surface.blit(text, (20, self.surface.get_height() // 2 - 20))

        if self.move_to_right:
            if time.time() - self.move_to_right > 0.1:
                text = pygame.font.Font(FONT_PATH, 30).render(f'▶', True, (0, 0, 0))
                self.surface.blit(text, (self.surface.get_width() - 50, self.surface.get_height() // 2 - 20))
        else:
            text = pygame.font.Font(FONT_PATH, 30).render(f'▶', True, (0, 0, 0))
            self.surface.blit(text, (self.surface.get_width() - 50, self.surface.get_height() // 2 - 20))

    def draw(self):
        # show parent view
        self.surface.fill(BACKGROUND_COLOR)

        if self.keyboard_state_controller.selected_parent:
            self.draw_child_keyboard()
        else:
            self.draw_keyboard()
        
        self.draw_camera_status()
        self.draw_triangle_gaze()

        if self.add_template_time is not None and time.time() - self.add_template_time < 3:
            self.draw_text(('追加しました。再起動して反映します。', (self.surface.get_width() // 2, self.surface.get_height() // 8), 30))
        
        pygame.display.update()
    
    def update(self):
        start_time = time.time()
        gestures: Gestures = None
        while not self.queue.empty():
            g, enqueued_at = self.queue.get()
            now = time.time()
            print(f'received gestures enqueued at: {datetime.fromtimestamp(enqueued_at)}, now: {datetime.fromtimestamp(now)}')
            if now - enqueued_at <= 0.3:
                gestures = g
                print(f'update gestures: {gestures}')
                break
            
        kind = self.keyboard_state_controller.kind
        keymap = KEYMAP[kind]['children'][self.keyboard_state_controller.current_parent_char]
        center_index = keymap.index(self.keyboard_state_controller.current_child_char)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    # print(self.keyboard_state_controller.selected_parent, keymap[center_index])
                    if not (self.keyboard_state_controller.selected_parent and keymap[center_index] == "定"):
                        self.keyboard_state_controller.select()
                if event.key == pygame.K_BACKSPACE:
                    self.keyboard_state_controller.back()
                if event.key == pygame.K_RETURN:
                    if self.keyboard_state_controller.text != "":
                        read_aloud(self.keyboard_state_controller.text)
                        self.keyboard_state_controller.clear()
                    self.keyboard_state_controller.clear()
                if event.key == pygame.K_a:
                    if self.keyboard_state_controller.text != "" and not self.keyboard_state_controller.selected_parent:
                        self.add_template_time = time.time()
                        add_template(self.keyboard_state_controller.text)
                        self.keyboard_state_controller.clear()
                if event.key == pygame.K_LEFT:
                    self.keyboard_state_controller.move(Direction.LEFT)
                if event.key == pygame.K_RIGHT:
                    self.keyboard_state_controller.move(Direction.RIGHT)
                if event.key == pygame.K_UP:
                    self.keyboard_state_controller.move(Direction.UP)
                if event.key == pygame.K_DOWN:
                    self.keyboard_state_controller.move(Direction.DOWN)

        if gestures is None:
            # イベントがなかったら更新処理をしない
            return 
        
        state_updated = False
        if self.delay <= 0:
            state_updated = self.updateKeyboardState(gestures)
        self.previous_gestures = gestures
        
        return state_updated
        
    def run(self):
        while True:
            start = time.time()

            self.draw()
            state_updated = self.update()

            frame_time = time.time() - start
            if state_updated:
                self.delay = MAX_DELAY
            else:
                self.delay = max(self.delay - frame_time, 0)

if __name__ == '__main__':
    queue = get_queue()
    Keyboard(queue).run()