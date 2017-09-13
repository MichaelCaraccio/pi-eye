from sensor_implementation.video_sensor import VideoSensor
import numpy as np
import time
import os
from subprocess import call
from picamera import PiCameraCircularIO
from sensehub_client.client import Client
from sensehub_client.value import Value
from multiprocessing import Process, Queue
import base64
import configparser


class PrintListener():

    # circular buffer time
    _CIRCULAR_BUFFER_TIME_S = 5
    # recording time after no motion is detected
    _RECORDING_TIME_S = 5

    # output format
    _FORMAT = "h264"
    # file extension for video saving
    _FILE_EXTENSION = "h264"

    _MOTION_COUNTER_THRESHOLD = 3

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
        self._motion_counter = 0
        client_video, client_image = create_clients('./config.ini')
        clients = {'image': client_image, 'video': client_video}
        self._upload_processes, self._message_queues = self._create_processes(
            clients)

        self._filename_video = ''

        self._last_uploaded = 0

        for process in self._upload_processes.values():
            print("starting process" + str(process))
            process.start()

        if not os.path.isdir(self._folderPath):
            os.mkdir(self._folderPath)

    def new_image(self, a, camera):
        if self._stream is None:
            self._stream = PiCameraCircularIO(
                camera, seconds=PrintListener._CIRCULAR_BUFFER_TIME_S, splitter_port=3)
            camera.start_recording(
                self._stream, splitter_port=3, format=PrintListener._FORMAT, sei=True, sps_timing=True)

        # waiting 2 seconds before trying to find motion so the camera has a
        # stable motion state
        if self._nbImages < PrintListener._STABILIZATION_TIME_S * camera.framerate:
            self._nbImages += 1
            return

        now = time.time()

        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        is_persistent = False

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('Motion detected!')
            self._last_time_motion = now
            self._motion_counter += 1
        elif now - self._last_time_motion > PrintListener._RECORDING_TIME_S:
            self._motion_counter = 0

        # Get image every _UPLOAD_TIME_S and convert to base 64
        if now - self._last_uploaded >= PrintListener._UPLOAD_TIME_S:
            filename_picture = self._folderPath +'/temp_image_' + str(now)
            camera.capture(filename_picture, 'jpeg',
                           use_video_port=True, quality=80)
            self._message_queues['image'].put(
                (filename_picture, is_persistent, 'image'))
            self._last_uploaded = now

        if now - self._last_time_motion <= PrintListener._RECORDING_TIME_S and self._motion_counter >= PrintListener._MOTION_COUNTER_THRESHOLD:
            if not self._is_camera_recording:
                self._filename_video = self._folderPath + \
                    '/frame%03d.%s' % (now, PrintListener._FILE_EXTENSION)
                self._file = open(self._filename_video, 'wb')

                self._stream.copy_to(self._file)
                self._stream.clear()

                self._is_camera_recording = True
                camera.start_recording(
                    self._file, splitter_port=2, format=PrintListener._FORMAT, sei=True, sps_timing=True)

                print('Writing %s' % self._filename_video)

        elif self._is_camera_recording:
            camera.stop_recording(splitter_port=2)
            self._file.close()
            self._is_camera_recording = False
            print('Recording stopped!')
            self._message_queues['video'].put(
                (self._filename_video, None, 'video'))

    def _create_processes(self, clients):
        processes = {}
        queues = {}
        for data_type, client in clients.items():
            queues[data_type] = Queue()
            processes[data_type] = Process(
                target=self._upload_method, args=(queues[data_type], client))
        return processes, queues

    def _convert_mp4(self, filename):
        filename_mp4 = filename +"_converted.mp4"
        command = "MP4Box -add %s %s" %(filename, filename_mp4)
        returncode = call(command.split(" "))
        if returncode != 0:
            return filename
        else:
            os.remove(filename)
            return filename_mp4

    def _upload_method(self, queue, client):
        while True:
            filename, is_persistent, data_type = queue.get()

            try:
                if data_type == 'video':
                    filename = self._convert_mp4(filename)

                value = Value(value=self._toBase64(filename),
                              type=data_type,
                              meta={'persist': is_persistent})
                status, message = client.new_value(value)
                if status:
                    print('Successfully uploaded : ' + data_type)
                    os.remove(filename)
                else:
                    print("Could not connect to server")
            finally:
                pass

    def _toBase64(self, filename):
        '''
        Convert image to base64
        :param filename: filename
        :return:
        '''
        with open(filename, 'rb') as img:
            return base64.b64encode(img.read()).decode('utf-8')


def create_clients(filename):
    '''
    i.e : create_client('./config.ini')
    '''

    try:
        config = configparser.ConfigParser()
        config.read(filename)

        server_ip = config.get("server", 'ip')
        server_port = config.get("server", 'port')

        sensor_id_video = config.get("sensor_video", 'sensor_id')
        key_video = config.get("sensor_video", 'key')

        sensor_id_image = config.get("sensor_picture", 'sensor_id')
        key_image = config.get("sensor_picture", 'key')

        return Client(server_ip, server_port, sensor_id_video, key_video), Client(server_ip, server_port, sensor_id_image, key_image)

    except FileExistsError:
        print("Error with file")
    except FileNotFoundError:
        print("File does not exist")
    except configparser.NoOptionError:
        print("Option does not exist")


def main():
    sensor = VideoSensor('videoTest')
    sensor.add(PrintListener())
    input("ENTER TO QUIT\n")


if __name__ == '__main__':
    main()
