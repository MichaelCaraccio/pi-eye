class EventManager(object):
    '''
    Abstract class that simplify the implementation of listeners
    '''

    def __init__(self, eventMethodName):
        '''
        :param eventMethodName: method called by the broadcast
        '''

        self._eventMethodName = eventMethodName
        self._listListener = {}

    def add(self, listener):
        '''
        Add a listener
        :param listener: object having a method named eventMethodName
        '''
        try:
            self._listListener[listener] = getattr(listener, self._eventMethodName)
        except AttributeError:
            print("Not the right method")

    def remove(self, listener):
        '''
        Remove a listener
        :param listener: object having a method named eventMethodName
        '''
        self._listListener.pop(listener)

    def _broadcast(self, *event):
        '''
        Must be call by the inherited classes when an event occures
        :param event: list of event parameters
        '''
        for method in self._listListener.values():
            method(*event)
