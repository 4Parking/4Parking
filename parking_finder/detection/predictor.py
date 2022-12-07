import cv2
import torch
import numpy as np

from typing import Tuple


class SpotPredictor:
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device='cpu')  # or yolov5n - yolov5x6, custom

    @staticmethod
    def ratio_overlap_parking_area(coord1: Tuple[int, int, int, int],
                                   coord2: Tuple[int, int, int, int]):
        '''
        Calculating ratio of area of parking spot,
        which is overlapped by detected object

        p: (xp1, yp1, xp2, yp2) - tuple of left upper coordinate and
        bottom right coordinate of parking spot
        d: (xd1, yd1, xd2, yd2) - tuple of left upper coordinate and
        bottom right coordinate of detected object
        '''
        xp1, yp1, xp2, yp2 = coord1
        xd1, yd1, xd2, yd2 = coord2
        dx = max(0, min(xp2, xd2) - max(xp1, xd1))
        dy = max(0, min(yp2, yd2) - max(yp1, yd1))
        opa = dx * dy
        area = (xp2 - xp1) * (yp2 - yp1)
        return opa / area

    def frame_processing(self, frame, grid, t=0.33):
        """
        Estimating load of parking on the frame

        :param frame: Numpy array; Picture of parking area
        :param grid: Numpy array; Coordinates of all parking spots
        :param t: float; threshold
        :return:
        """
        results = self.model(frame)
        d_coords = results.pred[0].numpy()[:, :4].astype(np.int32)
        is_available = [True] * len(grid)
        for i, p in enumerate(grid):
            for d in d_coords:
                r = SpotPredictor.ratio_overlap_parking_area(p, d)
                if r > t:
                    is_available[i] = False
                    continue
        return is_available, d_coords


    # def video_processing(source, grid, model, t=0.33):
    #     '''
    #     Estimating load of parking on the video stream
    #
    #     source: cv2.VideoCapture object; videostream from parking area
    #     grid: Numpy array; Coordinates of all parking spots
    #     model: torch.nn.Module; Model for object detection task
    #     t: float; threshold
    #     '''
    #     vrf = cv2.VideoWriter_fourcc(*'MP4V')
    #     vr = cv2.VideoWriter('result-full.mp4', vrf, 30.0, (720, 1280))
    #     while source.isOpened():
    #         # Capture frame-by-frame
    #         ret, frame = source.read()
    #         if ret == True:
    #             available_spots, d_coords = frame_processing(frame, grid, model, t)
    #             img = frame.copy()
    #             for p, a in zip(grid, available_spots):
    #                 x1, y1, x2, y2 = p
    #                 color = (0, 255, 0) if a else (0, 0, 255)
    #                 img = cv2.rectangle(img, (x1, y1), (x2, y2), color=color, thickness=2)
    #             vr.write(img)
    #         else:
    #             break






