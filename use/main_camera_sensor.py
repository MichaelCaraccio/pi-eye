from sensor_implementation.video_sensor import VideoSensor
import numpy as np
import time
import os
from picamera import PiCameraCircularIO
from sensehub_client.client import Client
from sensehub_client.value import Value
from multiprocessing import Process, Queue
import base64

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

    # time between each upload
    _UPLOAD_TIME_S = 3

    def __init__(self):
        self._folderPath = './generated'
        self._is_camera_recording = False
        self._last_time_motion = 0
        self._stream = None
        self._file = None
        self._nbImages = 0
        self._client = Client.create_client()
        self._message_queue = Queue()
        self._upload_process = Process(target=self._upload_method, args=(self._message_queue, self._client))

        self._last_uploaded = 0

        self._upload_process.start()

        if not os.path.isdir(self._folderPath):
            os.mkdir(self._folderPath)

    def new_image(self, a, camera):

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

        # Get image every _UPLOAD_TIME_S and convert to base 64

        now = time.time()

        if now - self._last_uploaded >= PrintListener._UPLOAD_TIME_S:
            filename = './temp_image_' + str(now)
            camera.capture(filename, 'jpeg', use_video_port=True, quality=80)
            self._message_queue.put(filename)
            self._last_uploaded = now

        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('Motion detected!', end='\r')
            self._last_time_motion = now

        if now - self._last_time_motion <= PrintListener._RECORDING_TIME_S:
            filename = self._folderPath + \
                '/frame%03d.%s' % (now, PrintListener._FILE_EXTENSION)

            if not self._is_camera_recording:
                self._file = open(filename, 'wb')

                self._stream.copy_to(self._file)
                self._stream.clear()

                self._is_camera_recording = True
                camera.start_recording(
                    self._file, splitter_port=2, format=PrintListener._FORMAT, sei=True, sps_timing=True)

                print('Writing %s' % filename)
        elif self._is_camera_recording:
            camera.stop_recording(splitter_port=2)
            self._file.close()
            self._is_camera_recording = False
            print('Recording stopped!')

    def _upload_method(self, queue, client):
        while True:
            filename = queue.get()
            print(filename)
            value = Value(value=self._toBase64(filename),
                          type="image",
                          meta=None)
            status, message = client.new_value(value)

            if not status == 'ok':
                print(message)
            else:
                print("Could not connect to server")
            os.remove(filename)

    def _toBase64(self, filename):
        '''
        Convert image to base64
        :param filename: filename
        :return:
        '''
        with open(filename, 'rb') as img:
            return base64.b64encode(img.read()).decode('utf-8')

def main():
    sensor = VideoSensor('videoTest')
    sensor.add(PrintListener())
    input("ENTER TO QUIT\n")


if __name__ == '__main__':
    main()
