from sensor_implementation.video_sensor import VideoSensor
import numpy as np
from PIL import Image
import time
import os


class PrintListener():
    _RECORDINGTIME = 10

    def __init__(self):
        self._folderPath = './generated'
        self._motionDetected = False
        self._lastTimeMotion = time.time()

        if not os.path.isdir(self._folderPath):
            os.mkdir(self._folderPath)

    def newImage(self, a, data):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion

        if (a > 60).sum() > 10:
            print('Motion detected!')
            self._lastTimeMotion = time.time()

        if time.time() - self._lastTimeMotion <= PrintListener._RECORDINGTIME:
            img = Image.fromarray(data)
            filename = self._folderPath + '/frame%03d.jpg' % time.time()
            print('Writing %s' % filename)
            img.save(filename, "JPEG", quality=80, optimize=True, progressive=True)


def main():
    sensor = VideoSensor('videoTest')
    sensor.add(PrintListener())

    input("ENTER TO QUIT")


if __name__ == '__main__':
    main()
