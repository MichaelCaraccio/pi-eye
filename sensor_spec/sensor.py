from sensor_spec.event_manager import EventManager


class Sensor(EventManager):
    '''
    Class describing the sensor that can handle and update a value when
    a value change from a call of _setValue
    '''
    def __init__(self, name, defaultValue, eventMethodName):
        '''
        :param name: sensor printable name
        :param defaultValue: default value
        :param eventMethodName: callable method name
        '''
        EventManager.__init__(self, eventMethodName)
        self._name = name
        self._value = defaultValue
        self._eventName = eventMethodName

    def getValue(self):
        '''
        Return last known value
        '''
        return self._value

    def _setValue(self, *values):
        '''
        Set one or more values and broadcast to all listeners
        :param value: values
        '''
        self._value = (values)
        self._broadcast(*values)
