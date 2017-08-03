class EventManager(object):
    '''
    Abstract class that simplify the implementation of listeners
    '''

    def __init__(self, event_method_name):
        '''
        :param event_method_name: method called by the broadcast
        '''

        self._event_method_name = event_method_name
        self._list_listener = {}

    def add(self, listener):
        '''
        Add a listener
        :param listener: object having a method named eventMethodName
        '''
        try:
            self._list_listener[listener] = getattr(
                listener, self._event_method_name)
        except AttributeError:
            print("Not the right method")

    def remove(self, listener):
        '''
        Remove a listener
        :param listener: object having a method named eventMethodName
        '''
        self._list_listener.pop(listener)

    def _broadcast(self, *event):
        '''
        Must be call by the inherited classes when an event occures
        :param event: list of event parameters
        '''
        for method in self._list_listener.values():
            method(*event)
