import statistics
import time

import cv2
import pygame
from sound_keyboard.sound.sound import (
    read_aloud
)

FONT_PATH = 'fonts/Noto_Sans_JP/NotoSansJP-Regular.otf'

def get_opencv_img_res(opencv_image):
    height, width = opencv_image.shape[:2]
    return width, height

def convert_opencv_img_to_pygame(opencv_image):
    """
    OpenCVの画像をPygame用に変換.

    see https://gist.github.com/radames/1e7c794842755683162b
    see https://github.com/atinfinity/lab/wiki/%5BOpenCV-Python%5D%E7%94%BB%E5%83%8F%E3%81%AE%E5%B9%85%E3%80%81%E9%AB%98%E3%81%95%E3%80%81%E3%83%81%E3%83%A3%E3%83%B3%E3%83%8D%E3%83%AB%E6%95%B0%E3%80%81depth%E5%8F%96%E5%BE%97
    """
    if len(opencv_image.shape) == 2:
        # グレイスケール画像の場合
        cvt_code = cv2.COLOR_GRAY2RGB
    else:
        # その他の場合:
        cvt_code = cv2.COLOR_BGR2RGB
    rgb_image = cv2.cvtColor(opencv_image, cvt_code).swapaxes(0, 1)
    # OpenCVの画像を元に、Pygameで画像を描画するためのSurfaceを生成する
    pygame_image = pygame.surfarray.make_surface(rgb_image)

    return pygame_image

def main():
    start_time = 0
    step = 0
    # OpenCVで画像を読み込む
    webcam = cv2.VideoCapture(1)    # 環境によって引数の値を変える
    _, opencv_image = webcam.read()

    # Pygameを初期化
    pygame.init()
    width, height = get_opencv_img_res(opencv_image)
    screen = pygame.display.set_mode((width, height))

    while True:
        # OpenCVで画像を読み込む
        _, opencv_image = webcam.read()

        # OpenCVの画像をPygame用に変換
        pygame_image = convert_opencv_img_to_pygame(opencv_image)

        # 画像を左右反転する
        pygame_image = pygame.transform.flip(pygame_image, True, False)

        # 画像を縮小
        pygame_image = pygame.transform.scale(pygame_image, (width // 3, height // 3))

        # 背景色を白にする
        screen.fill((255, 255, 255))

        # Pygameで画像を中央に表示
        screen.blit(pygame_image, (width // 2 - pygame_image.get_width() // 2, 0))

        # 画面中央上部に円を表示
        # pygame.draw.ellipse(screen, (240, 240, 240), (width // 2 - 50, 50, 100, 100), 5)

        # Enterが押されたら
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_time = 0  # 0で初期化
                    step += 1

        # stepで処理を分岐させる
        # 文字を表示
        font = pygame.font.Font(FONT_PATH, 30)
        # 初期状態
        if step == 0:
            text = font.render('顔を円の位置に合わせてください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
        # 右
        elif step == 1:
            if not start_time: start_time = time.time() # 開始時間を記録
            text = font.render('右の数字を見てください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.9, height // 2), 10)
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30)) #カウントダウンを中央に表示
                screen.blit(text, (width * 0.9, height // 2)) #カウントダウンを右に表示
            else:
                step += 1
                start_time = 0
        # 左
        elif step == 2:
            if not start_time: start_time = time.time()
            text = font.render('左の数字を見てください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.1, height // 2), 10)
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30))
                screen.blit(text, (width * 0.1, height // 2)) #カウントダウンを左に表示
            else:
                step += 1
                start_time = 0
        # 目を閉じる
        elif step == 3:
            if not start_time: start_time = time.time()
            text = font.render('目を閉じてください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30))
                screen.blit(text, (width // 2, height // 2 + 30)) #カウントダウンを左に表示
            else:
                read_aloud("終了です")
                step += 1
                start_time = 0
        # 終了
        elif step == 4:
            text = font.render('終了', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))

        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == '__main__':
    main()