from sensor_implementation.video_sensor import VideoSensor
import numpy as np
import time
import os
from picamera import PiCameraCircularIO


class PrintListener():

    # circular buffer time
    _CIRCULAR_BUFFER_TIME_S = 5
    # recording time after no motion is detected
    _RECORDING_TIME_S = 1

    # output format
    _FORMAT = "h264"
    # file extension for video saving
    _FILE_EXTENSION = "h264"

    # time before the motion sensing is activated, allows the camera to have a
    # "stable" motion matrix
    _STABILIZATION_TIME_S = 2

    def __init__(self):
        self._folderPath = './generated'
        self._isCameraRecording = False
        self._lastTimeMotion = 0
        self._stream = None
        self._file = None
        self._nbImages = 0

        if not os.path.isdir(self._folderPath):
            os.mkdir(self._folderPath)

    def newImage(self, a, camera):
        if self._stream is None:
            self._stream = PiCameraCircularIO(
                camera, seconds= PrintListener._CIRCULAR_BUFFER_TIME_S, splitter_port=3)
            camera.start_recording(
                self._stream, splitter_port=3, format=PrintListener._FORMAT, sei=True, sps_timing=True)

        # waiting 2 seconds before trying to find motion so the camera has a
        # stable motion state
        if self._nbImages < PrintListener._STABILIZATION_TIME_S * camera.framerate:
            self._nbImages += 1
            return

        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('Motion detected!', end='\r')
            self._lastTimeMotion = time.time()

        if time.time() - self._lastTimeMotion <= PrintListener._RECORDING_TIME_S:
            filename = self._folderPath + \
                '/frame%03d.%s' % (time.time(),
                                   PrintListener._FILE_EXTENSION)

            if not self._isCameraRecording:
                self._file = open(filename, 'wb')

                self._stream.copy_to(self._file)
                self._stream.clear()

                self._isCameraRecording = True
                camera.start_recording(
                    self._file, splitter_port=2, format=PrintListener._FORMAT, sei=True, sps_timing=True)

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
    input("ENTER TO QUIT\n")


if __name__ == '__main__':
    main()
