import cv2
import csv
from sound_keyboard.face_gesture_detector.gaze_tracking import GazeTracking
import pyautogui as pag
import pygame
from sound_keyboard.sound.sound import (read_aloud)
from sound_keyboard.read_camera_num import read_camera_num
import time
import statistics

FONT_PATH = 'fonts/Noto_Sans_JP/NotoSansJP-Regular.otf'
csv_name = 'gaze_threshold.csv'


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


def save_to_csv(average_list):
    with open(csv_name, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(average_list)
    print('save_to_csv')


def get_mean(threshold_list, is_ratio):
    list_filtered = [x for x in threshold_list if x is not None]

    if is_ratio:
        mean_num = statistics.harmonic_mean(list_filtered)
    else:
        mean_num = statistics.mean(list_filtered)

    return mean_num


def main():
    start_time = 0
    step = 0
    # gazeクラスをたてる
    gaze = GazeTracking()
    # OpenCVで画像を読み込む
    webcam = cv2.VideoCapture(read_camera_num())
    _, opencv_image = webcam.read()

    # Pygameを初期化
    pygame.init()
    cam_w, cam_h = get_opencv_img_res(opencv_image)
    width, height = pag.size()
    screen = pygame.display.set_mode((width, height))
    cam_ratio = height * 0.4 / cam_h
    cam_view_size_w = int(cam_w * cam_ratio)
    cam_view_size_h = int(cam_h * cam_ratio)

    right_ratio = []
    left_ratio = []
    blinkings = []
    mouth_ratio = []

    pupil_located = 0

    while True:
        # OpenCVで画像を読み込む
        _, opencv_image = webcam.read()

        gaze.refresh(opencv_image)
        opencv_image = gaze.annotated_frame()

        # OpenCVの画像をPygame用に変換
        pygame_image = convert_opencv_img_to_pygame(opencv_image)

        # 画像を左右反転する
        pygame_image = pygame.transform.flip(pygame_image, True, False)

        # 画像を縮小
        pygame_image = pygame.transform.scale(pygame_image, (cam_view_size_w, cam_view_size_h))

        # 背景色を白にする
        screen.fill((255, 255, 255))

        # Pygameで画像を中央に表示
        screen.blit(pygame_image, (width // 2 - pygame_image.get_width() // 2, 0))

        # Enterが押されたら
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_time = 0
                    step += 1

        # 文字を表示
        font = pygame.font.Font(FONT_PATH, 30)

        # step0(顔の認証を行う)
        if step == 0:
            if not start_time: start_time = time.time()
            text = font.render('セットアップを始めます', True, (0, 0, 0))
            pygame.draw.ellipse(screen, (255), (
            width // 2 - cam_view_size_h * 0.3, cam_view_size_h * 0.2, cam_view_size_h * 0.6, cam_view_size_h * 0.6), 5)
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('顔を円の中に入れ、正面を向いたまま、目線のみ動かしてください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            text = font.render('右を見る、左を見る、目を瞑るの順でキャリブレーションを行います', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 100))
            text = font.render('Step 0/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 150))
            if gaze.pupils_located:
                pupil_located += 1
            else:
                pupil_located = 0
            print(pupil_located)
            if pupil_located >= 30 and time.time() - start_time >= 8:
                step += 1
                start_time = 0

        # step1(右を開始する)
        elif step == 1:
            if not start_time: start_time = time.time()
            text = font.render('顔を検知しました。キャリブレーションを開始します', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 1/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # 4秒カウントダウンする
            if time.time() - start_time < 4:
                text = font.render(str(4 - int(time.time() - start_time)), True, (0, 0, 0))
                screen.blit(text, (width, height // 2 + 100))
            else:
                step += 1
                start_time = 0

        # step1(右を見た時の閾値を決定)
        elif step == 2:
            if not start_time: start_time = time.time()
            text = font.render('正面を向いたまま、右の数字を見てください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 1/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.9, height // 2), 10)
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30)) #カウントダウンを中央に表示
                screen.blit(text, (width * 0.9, height // 2))  # カウントダウンを右に表示
                if time.time() - start_time < 3:
                    right_ratio.append(gaze.horizontal_ratio())
                    mouth_ratio.append(gaze.lips_ratio())
            else:
                step += 1
                start_time = 0

        # step2(右と左の間の時間)
        elif step == 3:
            if not start_time: start_time = time.time()
            text = font.render('続いて、左の測定を行います', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 2/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.1, height // 2), 10)
            # 4秒カウントダウンする
            if time.time() - start_time < 4:
                text = font.render(str(4 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30)) #カウントダウンを中央に表示
                screen.blit(text, (width, height // 2))
            else:
                step += 1
                start_time = 0

        # step2(左を見た時の閾値を決定)
        elif step == 4:
            if not start_time: start_time = time.time()
            text = font.render('正面を向いたまま、左の数字を見てください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 2/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.1, height // 2), 10)
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30))
                screen.blit(text, (width * 0.1, height // 2))  # カウントダウンを左に表示
                if time.time() - start_time < 3:
                    left_ratio.append(gaze.horizontal_ratio())
            else:
                step += 1
                start_time = 0

        # step3(右と閉じるの間の時間)
        elif step == 5:
            if not start_time: start_time = time.time()
            text = font.render('続いて、目と口を閉じる測定を行います。終了時にアナウンスします', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 3/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # pygame.draw.circle(screen, (0, 0, 0), (width * 0.1, height // 2), 10)
            # 4秒カウントダウンする
            if time.time() - start_time < 4:
                text = font.render(str(4 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30)) #カウントダウンを中央に表示
                screen.blit(text, (width, height // 2))
            else:
                step += 1
                start_time = 0

        # step3(目をつむったときの閾値を設定)
        elif step == 6:
            if not start_time: start_time = time.time()
            text = font.render('正面を向いたまま、目と口を閉じてください', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
            text = font.render('Step 3/3', True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            # 10秒カウントダウンする
            if time.time() - start_time < 10:
                text = font.render(str(10 - int(time.time() - start_time)), True, (0, 0, 0))
                # screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 30))
                screen.blit(text, (width // 2, height // 2 + 100))  # カウントダウンを左に表示
                if time.time() - start_time < 3:
                    blinkings.append(gaze.blinking_ratio())
            else:
                read_aloud("終了です")
                step += 1
                start_time = 0

        # step5(終了＆閾値の平均を保存)
        elif step == 7:
            if time.time() - start_time < 5:
                text = font.render('終了', True, (0, 0, 0))
                screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
                text = font.render('Step 3/3', True, (0, 0, 0))
                screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 + 50))
            else:
                print(mouth_ratio)
                save_to_csv([get_mean(right_ratio, is_ratio=False), get_mean(left_ratio, is_ratio=False), get_mean(blinkings, is_ratio=True), get_mean(mouth_ratio, is_ratio=True)])
                return

        # 画面更新
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return


if __name__ == '__main__':
    main()
