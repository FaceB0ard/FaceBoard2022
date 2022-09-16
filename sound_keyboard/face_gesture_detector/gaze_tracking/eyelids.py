import numpy as np
from imutils import face_utils

LEFT_POINTS = [36, 37, 38, 39, 40, 41]
RIGHT_POINTS = [42, 43, 44, 45, 46, 47]

class Eyelids(object):
    def __init__(self, landmarks, side):
        self.landmarks = face_utils.shape_to_np(landmarks)
        self.width = None
        self.height = None

        self._analyze(self.landmarks, side)
    
    def _analyze(self, landmarks, side):
        if side == 0:
            points = LEFT_POINTS
        elif side == 1:
            points = RIGHT_POINTS
        self.width = self._eyelibs_width(landmarks, points)
        self.height = self._eyelibs_height(landmarks, points)

    def _eyelibs_width(self, landmarks, points):
        return abs(landmarks[points[0]][0] - landmarks[points[3]][0])

    def _eyelibs_height(self, landmarks, points):
        top_lip = landmarks[points[1:3]]
        low_lip = landmarks[points[4:6]]

        top_mean = np.mean(top_lip, axis=0)
        low_mean = np.mean(low_lip, axis=0)

        eyelibs_dist = abs(top_mean[1] - low_mean[1])
        return eyelibs_dist