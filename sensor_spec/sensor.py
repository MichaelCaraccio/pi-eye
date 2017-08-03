from sensor_spec.event_manager import EventManager


class Sensor(EventManager):
    '''
    Class describing the sensor that can handle and update a value when
    a value change from a call of _setValue
    '''

    def __init__(self, name, default_value, event_method_name):
        '''
        :param name: sensor printable name
        :param default_value: default value
        :param event_method_name: callable method name
        '''
        EventManager.__init__(self, event_method_name)
        self._name = name
        self._value = default_value
        self._event_name = event_method_name

    def get_value(self):
        '''
        Return last known value
        '''
        return self._value

    def _set_value(self, *values):
        '''
        Set one or more values and broadcast to all listeners
        :param value: values
        '''
        self._value = (values)
        self._broadcast(*values)
