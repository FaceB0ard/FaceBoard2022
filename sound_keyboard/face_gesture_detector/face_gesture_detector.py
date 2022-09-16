import time
import copy
import numpy as np
from math import hypot

from sound_keyboard.queue import get_queue
from sound_keyboard.face_gesture_detector.enums import (
    EyeDirection,
    EyeState,
    MouthState,
    Gestures
)

import cv2
import dlib

from sound_keyboard.face_gesture_detector.gaze_tracking import GazeTracking


class FaceGestureDetector:

    def __init__(self, queue):
        self.cap = cv2.VideoCapture(0)
        self.queue = queue
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(
            "./sound_keyboard/face_gesture_detector/shape_predictor_68_face_landmarks.dat")
        # self.debug = len(sys.argv) >= 2 and sys.argv[1] == 'DEBUG'
        self.debug = True

        self.previous = None

        self.gaze = GazeTracking()

    def get_gaze_state(self, x):
        if x <= 0.54:
            return EyeDirection.LEFT
        if x >= 0.57:
            return EyeDirection.RIGHT
        return EyeDirection.CENTER

    def get_mouth_state(self, mouth_ratio):
        if mouth_ratio > 6.8:
            return MouthState.CLOSE
        else:
            return MouthState.OPEN

    # ランドマークの重心
    def midpoint(self, p1, p2):
        return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

    # 口開閉検知
    def get_mouth_ratio(self, eye_points, facial_landmarks):
        mouth_region = np.array([
            (
                facial_landmarks.part(eye_points[0]).x,
                facial_landmarks.part(eye_points[0]).y
            ),
            (
                facial_landmarks.part(eye_points[1]).x,
                facial_landmarks.part(eye_points[1]).y
            ),
            (
                facial_landmarks.part(eye_points[2]).x,
                facial_landmarks.part(eye_points[2]).y
            ),
            (
                facial_landmarks.part(eye_points[3]).x,
                facial_landmarks.part(eye_points[3]).y
            ),
            (
                facial_landmarks.part(eye_points[4]).x,
                facial_landmarks.part(eye_points[4]).y
            ),
            (
                facial_landmarks.part(eye_points[5]).x,
                facial_landmarks.part(eye_points[5]).y
            )], np.int32)
        left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = self.midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
        center_bottom = self.midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

        # hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
        # ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

        hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
        ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

        if ver_line_length == 0:
            ver_line_length += 0.001

        ratio = hor_line_length / ver_line_length
        return ratio, mouth_region

    # 視線検知
    def get_gaze_right_level(self, eye_points, facial_landmarks, frame, gray):
        left_eye_region = np.array([
            (
                facial_landmarks.part(eye_points[0]).x,
                facial_landmarks.part(eye_points[0]).y
            ),
            (
                facial_landmarks.part(eye_points[1]).x,
                facial_landmarks.part(eye_points[1]).y
            ),
            (
                facial_landmarks.part(eye_points[2]).x,
                facial_landmarks.part(eye_points[2]).y
            ),
            (
                facial_landmarks.part(eye_points[3]).x,
                facial_landmarks.part(eye_points[3]).y
            ),
            (
                facial_landmarks.part(eye_points[4]).x,
                facial_landmarks.part(eye_points[4]).y
            ),
            (
                facial_landmarks.part(eye_points[5]).x,
                facial_landmarks.part(eye_points[5]).y
            )], np.int32)

        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)
        cv2.polylines(mask, [left_eye_region], True, 255, 2)
        cv2.fillPoly(mask, [left_eye_region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)

        min_x = np.min(left_eye_region[:, 0])
        max_x = np.max(left_eye_region[:, 0])
        min_y = np.min(left_eye_region[:, 1])
        max_y = np.max(left_eye_region[:, 1])

        gray_eye = eye[min_y: max_y, min_x: max_x]
        _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
        height, width = threshold_eye.shape
        left_side_threshold = threshold_eye[0: height, int(width / 2): width]
        left_side_white = cv2.countNonZero(left_side_threshold)

        right_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
        right_side_white = cv2.countNonZero(right_side_threshold)

        under_side_threshold = threshold_eye[int(height / 2):height, 0:width]
        under_side_white = cv2.countNonZero(under_side_threshold)

        if left_side_white == 0:
            gaze_right_level = 0
        elif right_side_white == 0:
            gaze_right_level = 1
        else:
            gaze_right_level = left_side_white / (right_side_white + left_side_white)

        return gaze_right_level, under_side_white, left_eye_region

    def gaze_preprocess(self, frame, face):

        # ランドマーク
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        landmarks = self.predictor(gray, face)
        return landmarks, gray

    def get_eye_blink_state(self, frame, landmarks, facial_landmarks):
        x = [0 for i in range(len(facial_landmarks))]
        y = [0 for i in range(len(facial_landmarks))]

        for i, facial_landmark in enumerate(facial_landmarks):
            x[i] = landmarks.part(facial_landmark).x
            y[i] = landmarks.part(facial_landmark).y

        trim_val = 2
        frame_trim = frame[y[1] - trim_val:y[3] + trim_val, x[0]:x[2]]
        height, width = frame_trim.shape[0], frame_trim.shape[1]
        frame_trim_resize = cv2.resize(frame_trim, (int(width * 7.0), int(height * 7.0)))
        # gray scale
        frame_gray = cv2.cvtColor(frame_trim_resize, cv2.COLOR_BGR2GRAY)
        # 平滑化
        frame_gray = cv2.GaussianBlur(frame_gray, (7, 7), 0)
        # 二値化
        thresh = 80
        maxval = 255
        e_th, frame_black_white = cv2.threshold(frame_gray, thresh, maxval, cv2.THRESH_BINARY_INV)
        eye_contours, _ = cv2.findContours(frame_black_white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(eye_contours) == 0:
            return EyeState.CLOSE

        return EyeState.OPEN

    def run(self):
        # この関数のwhile True:下でcapから画像を取得して、ジェスチャーを判別、
        # queueに(Gestureオブジェクト、time.time())の形でジェスチャーを入れていってください。
        while True:
            _, frame = self.cap.read()
            self.gaze.refresh(frame)
            frame = self.gaze.annotated_frame()

            # まばたきの計測
            # left_eye_state, right_eye_state, left_eye_position, right_eye_position = get_eye_state(frame, landmarks)
            if self.gaze.is_blinking():
                left_eye_state = EyeState.CLOSE
                right_eye_state = EyeState.CLOSE
            else:
                left_eye_state = EyeState.OPEN
                right_eye_state = EyeState.OPEN

            eye_direction = EyeDirection.CENTER
            if self.gaze.is_right():
                eye_direction = EyeDirection.RIGHT
            elif self.gaze.is_left():
                eye_direction = EyeDirection.LEFT
            else:
                eye_direction = EyeDirection.CENTER

            if self.gaze.is_mouth_open():
                mouth_state = MouthState.OPEN
            else:
                mouth_state = MouthState.CLOSE

            if self.debug:

                def draw_eye(frame):
                    # direction
                    right_x = landmarks.part(41).x
                    right_y = landmarks.part(41).y
                    left_x = landmarks.part(46).x
                    left_y = landmarks.part(46).y
                    if eye_direction == EyeDirection.RIGHT:
                        text = "->"
                    elif eye_direction == EyeDirection.RIGHT:
                        text = "<-"
                    else:
                        text = "o"

                    cv2.putText(frame, text, (right_x, right_y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    cv2.putText(frame, text, (left_x, left_y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                    # state
                    right_x = landmarks.part(36).x
                    right_y = landmarks.part(36).y
                    left_x = landmarks.part(42).x
                    left_y = landmarks.part(42).y
                    if left_eye_state == EyeState.OPEN:
                        text = "OPEN"
                    elif left_eye_state == EyeState.CLOSE:
                        text = "CLOSE"
                    else:
                        text = "None"

                    cv2.putText(frame, text, (right_x - 10, right_y - 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    cv2.putText(frame, text, (left_x - 10, left_y - 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                def draw_mouth(frame):
                    mouth_landmarks = []
                    for n in range(48, 59):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        mouth_landmarks.append((x, y))
                        next_point = n + 1
                        if n == 47:
                            next_point = 42
                        x2 = landmarks.part(next_point).x
                        y2 = landmarks.part(next_point).y
                        cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)
                    cv2.line(frame, (landmarks.part(59).x, landmarks.part(59).y),
                             (landmarks.part(48).x, landmarks.part(48).y), (0, 255, 0), 1)

                    if mouth_state == MouthState.CLOSE:
                        text = "CLOSE"
                    else:
                        text = "OPEN"
                    cv2.putText(frame, text, (landmarks.part(54).x, landmarks.part(54).y), cv2.FONT_HERSHEY_PLAIN, 2,
                                (255, 0, 0), 2)

                if self.debug:

                    frame_flip = cv2.flip(frame, 1)

                    # メモリ削減のためグレースケールか
                    gray = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2GRAY)

                    # 画面上の全ての顔検知(四隅の点の座標を取得)
                    faces = self.detector(gray)

                    # 複数の顔全てに対して
                    for face in faces:
                        # 『顔の四隅』を描写する処理
                        # 四隅の座標取得
                        x, y = face.left(), face.top()
                        x1, y1 = face.right(), face.bottom()
                        # 四角形描写（GUIライブラリにありがちな方法やね）
                        cv2.rectangle(frame_flip, (x, y), (x1, y1), (0, 0, 255))

                for face in faces:
                    # 『ランドマーク』を描写する処理
                    landmarks = self.predictor(gray, face)
                    draw_eye(frame_flip)
                    draw_mouth(frame_flip)

                cv2.imshow("debug", frame_flip)

                # エスケープキーでループを抜ける処理
                key = cv2.waitKey(1)  # キーの入力を()の中msだけ受け取る and ウィンドウがぶつ切りになるのを防ぐ
                if key == 27:  # 27がエスケープキーに対応
                    break

            if self.queue.full():
                self.queue.queue.clear()

            gestures = Gestures(
                eye_direction=eye_direction,
                left_eye_state=left_eye_state,
                right_eye_state=right_eye_state,
                mouth_state=mouth_state,
            )

            # queueに投げるの分岐させてもいいかも
            self.queue.put((gestures, time.time()))
            print(gestures)

            self.previous = copy.deepcopy(gestures)


if __name__ == '__main__':
    queue = get_queue()
    FaceGestureDetector(queue).run()
