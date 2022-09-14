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
MAX_DELAY = 0.5

FONT_PATH = 'fonts/Noto_Sans_JP/NotoSansJP-Regular.otf'

class Keyboard:
    def __init__(self, queue):

        self.queue = queue
        # initialize app
        pygame.init()
        pygame.display.set_caption('FaceBoard')

        # setting initial window size and set window resizable
        self.surface = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

        # setting keyboard controller
        self.keyboard_state_controller = KeyboardStateController()

        # state
        self.previous_gestures = None
        self.delay = 0

        self.add_template_time = None
    
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
        cell_sizes = [70, 30, 10]
        font_sizes = [70, 30, 10]
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
                    keymap[index] if abs(dir) != 2 else '...',
                    (width // 2 +  sign * distance, height // 2),
                    cell_size,
                    KEYTILE_COLOR,
                    0,
                    font_size
                )
        
        # draw currently selected text
        self.draw_text((self.keyboard_state_controller.text, (width / 2, height * 7 // 8), 20))

    def updateKeyboardState(self, gestures: Gestures):

        # Gesturesオブジェクトの状態を読み出して操作を確定する
        print(gestures.eye_direction)
        if  gestures.eye_direction != EyeDirection.CENTER:
            direction = convert_eye_direction_to_direction(gestures.eye_direction)
            self.keyboard_state_controller.move(direction)
            print(f"move {direction}")
            return True
        
        if (self.previous_gestures is None or self.previous_gestures.left_eye_state == EyeState.OPEN) and gestures.left_eye_state == EyeState.CLOSE:
            # back
            self.keyboard_state_controller.back()
            return True
        
        if (self.previous_gestures is None or self.previous_gestures.right_eye_state == EyeState.OPEN) and gestures.right_eye_state == EyeState.CLOSE:
            # select
            self.keyboard_state_controller.select()
            return True
        
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

        cell_sizes = [70, 40, 30]
        font_sizes = [50, 20, 10]
        distances = [0, base // 2, base * 4 // 5]

        center_index = keymap.index(self.keyboard_state_controller.current_child_char)

        # draw currently selected text
        self.draw_text((self.keyboard_state_controller.text, (width / 2, height * 7 // 8), 20))

        # 描画順を変えてみる
        # for dir in range(-2, 3):
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
                        keymap[index] if abs(dir) != 2 else '...',
                        (width // 2 +  sign * distance, height // 3),
                        cell_size,
                        KEYTILE_COLOR,
                        0,
                        font_size
                    )
        
        

    def draw(self):

        # show parent view
        self.surface.fill(BACKGROUND_COLOR)

        if self.keyboard_state_controller.selected_parent:
            self.draw_child_keyboard()
        else:
            self.draw_keyboard()
        
        if self.add_template_time is not None and time.time() - self.add_template_time < 3:
            self.draw_text(('追加しました。再起動して反映します。', (self.surface.get_width() // 2, self.surface.get_height() // 8), 20))
        
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
                break

        if gestures is not None:
            pass
            # イベントがあったらキーボードの状態を更新する
            """gestures = Gestures(
                eye_direction = EyeDirection.CENTER,
                left_eye_state = EyeState.OPEN,
                right_eye_state = EyeState.OPEN,
                mouth_state = MouthState.CLOSE,
            )"""
            
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
            
        """#TODO(hakomori64) remove it 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.keyboard_state_controller.move(Direction.LEFT)
            # gestures.eye_direction = EyeDirection.LEFT
        if keys[pygame.K_UP]:
            self.keyboard_state_controller.move(Direction.UP)
            # gestures.eye_direction = EyeDirection.UP
        if keys[pygame.K_RIGHT]:
            self.keyboard_state_controller.move(Direction.RIGHT)
            # gestures.eye_direction = EyeDirection.RIGHT
        if keys[pygame.K_DOWN]:
            self.keyboard_state_controller.move(Direction.DOWN)
            # gestures.eye_direction = EyeDirection.DOWN
        if keys[pygame.K_PAGEDOWN]:
            self.keyboard_state_controller.select()
            # gestures.left_eye_state = EyeState.CLOSE
        if keys[pygame.K_PAGEUP]:
            self.keyboard_state_controller.back()
            #gestures.right_eye_state = EyeState.CLOSE
        if keys[pygame.K_RETURN]:
            self.keyboard_state_controller.clear()
            #gestures.mouth_state = MouthState.OPEN
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()"""
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