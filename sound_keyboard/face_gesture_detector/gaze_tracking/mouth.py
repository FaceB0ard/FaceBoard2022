import numpy as np
from imutils import face_utils

MOUTH_POINTS = [60, 61, 62, 63, 64, 65, 66, 67]

class Mouth(object):
    def __init__(self, landmarks):
        self.landmarks = face_utils.shape_to_np(landmarks)
        self.width = None
        self.height = None

        self._analyze(self.landmarks)
    
    def _analyze(self, landmarks):
        self.width = self._mouth_width(landmarks, MOUTH_POINTS)
        self.height = self._mouth_height(landmarks, MOUTH_POINTS)

    def _mouth_width(self, landmarks, points):
        return abs(landmarks[points[0]][0] - landmarks[points[4]][0])

    def _mouth_height(self, landmarks, points):
        top_lip = landmarks[points[1:4]]
        low_lip = landmarks[points[5:8]]

        top_mean = np.mean(top_lip, axis=0)
        low_mean = np.mean(low_lip, axis=0)

        lip_dist = abs(top_mean[1] - low_mean[1])
        return lip_dist