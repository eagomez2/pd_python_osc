import threading
import random
import time
from collections import namedtuple

from datetime import datetime, timedelta
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

from apscheduler.schedulers.background import BackgroundScheduler

SocketAddress = namedtuple('SocketAddress', ['ip', 'port'])


class OSCSender(threading.Thread):
    """ Class for sending OSC messages from python to Pd.

    This class establishes a connection with Pd server on ip address and port.
    """

    def __init__(self, ip='127.0.0.1', port=8888, ticks_queue=None, playback_sequence_queue=None):
        super().__init__()
        self.setDaemon(True)
        self._socket_address = SocketAddress(ip, port)
        self.ticks_queue = ticks_queue
        self.playback_sequence_queue = playback_sequence_queue
        self.client = SimpleUDPClient(*self._socket_address)

    @property
    def socket_address(self):
        return self._socket_address


    @socket_address.setter
    def socket_address(self, value):
        try:
            ip, port = value
        except TypeError:
            raise TypeError('You must provide an (ip, port) tuple')
        else:
            self._socket_address = SocketAddress(ip, port)
    

    @property
    def ip(self):
        return self._socket_address.ip
    

    @property
    def port(self):
        return self._socket_address.port
    

    def run(self):
        (start_tick, pitch, velocity, duration) = (None, None, None, None)
        while True:
            if start_tick is None:  # If no note to play, wait for a new note
                (start_tick, pitch, velocity, duration) = self.playback_sequence_queue.get()
            else:
                current_tick = self.ticks_queue.get()

                if current_tick == start_tick:
                    self.send('/note', [pitch, velocity, duration])
                    (start_tick, pitch, velocity, duration) = (None, None, None, None)

    
    def send(self, address, value):
        self.client.send_message(address, value)



class OSCReceiver(threading.Thread):

    def __init__(self, ip='127.0.0.1', port=8888, quit_event=None, address_list=['/clock*'], address_handler_list=[None]):
        super().__init__()  # Run constructor of parent class
        self.setDaemon(True)
        self._socket_address = SocketAddress(ip, port)
        self.listening_thread = None
        self.dispatcher = Dispatcher()


        # Map addresses to handlers
        if len(address_list) != len(address_handler_list):
            raise TypeError('address_list and address_handler list must have the same length')

        for address, handler in zip(address_list, address_handler_list):
            self.dispatcher.map(address, handler)
        
        # Set default handler for unmatched addresses
        self.dispatcher.set_default_handler(self.default_handler)

        # Get OSC UDP server instance
        self.server = BlockingOSCUDPServer(self._socket_address, self.dispatcher)

        # Invoked upon quit event
        self.quit_event = quit_event


    @property
    def socket_address(self):
        return self._socket_address


    @socket_address.setter
    def socket_address(self, value):
        try:
            ip, port = value
        except TypeError:
            raise TypeError('You must provide an (ip, port) tuple')
        else:
            self._socket_address = SocketAddress(ip, port)


    @property
    def ip(self):
        return self._socket_address.ip
    

    @property
    def port(self):
        return self._socket_address.port


    def run(self):
        print(f'Listening incoming OSC message on port {self.port}\n')
        msg_count = 0

        while not self.quit_event.is_set():
            self.server.handle_request()

    
    def default_handler(self, address, *args):
        print(f'Default handler called with {address} {args}')