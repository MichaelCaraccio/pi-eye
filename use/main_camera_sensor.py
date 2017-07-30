from sensor_implementation.video_sensor import VideoSensor
import numpy as np
import time
import os
from picamera import PiCameraCircularIO


class PrintListener():
    _RECORDINGTIME = 1

    def __init__(self):
        self._folderPath = './generated'
        self._isCameraRecording = False
        self._lastTimeMotion = 0
        self._stream = None
        self._file = None

        if not os.path.isdir(self._folderPath):
            os.mkdir(self._folderPath)

    def newImage(self, a, camera):
        print("newImage")

        if self._stream is None:
            self._stream = PiCameraCircularIO(camera, seconds=5, splitter_port=3)
            camera.start_recording(self._stream, format='h264', splitter_port=3)

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
            filename = self._folderPath + '/frame%03d.h264' % time.time()

            if not self._isCameraRecording :
                self._file = open(filename, 'wb')

                self._stream.copy_to(self._file)
                self._stream.clear()

                self._isCameraRecording = True
                camera.start_recording(self._file, format='h264', splitter_port=2)

                #camera.capture(filename, 'jpeg', use_video_port=True, quality=80)
                print('Writing %s' % filename)
        elif self._isCameraRecording:
                camera.stop_recording(splitter_port=2)
                self._file.close()
                self._isCameraRecording = False
                print('Recording stopped!')

def main():
    sensor = VideoSensor('videoTest')
    sensor.add(PrintListener())

    input("ENTER TO QUIT")


if __name__ == '__main__':
    main()
