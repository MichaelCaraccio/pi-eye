from sensor_spec.sensor import Sensor
import picamera
import picamera.array
from picamera.array import PiMotionAnalysis
from picamera.encoders import PiEncoder

class VideoSensor(Sensor, PiMotionAnalysis):
    '''
    Video sensor is an inherited class of sensor which uses the camera
    '''

    def __init__(self, name):
        '''

        :param name: displayable name of the sensor
        '''
        Sensor.__init__(self, name, None, 'new_image')

        self._w = int(1280)
        self._h = int(720)
        self._framerate = 5
        self._camera = picamera.PiCamera()

        PiMotionAnalysis.__init__(self, self._camera)

        self._camera.resolution = (self._w, self._h)
        self._camera.framerate = self._framerate
        self._camera.start_recording(
            '/dev/null', format='h264', motion_output=self, sps_timing=True, sei=True)

    def analyze(self, motion_matrix):
        '''
        Callback method for PiMotionAnalysis
        :param motion_matrix: motion matrix
        '''
        self._set_value(motion_matrix, self._camera)

    def stop(self):
        '''
        Stop recording
        '''
        self._camera.stop_recording()
