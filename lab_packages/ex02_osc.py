import time
import threading
from collections import namedtuple
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

SocketAddress = namedtuple('SocketAddress', ['ip', 'port'])

class OSCReceiver(threading.Thread):

    def __init__(self, ip='127.0.0.1', port=8889, quit_event=None, address_list=['/clock*'], address_handler_list=[None]):
        super().__init__()  # Run constructor of parent class
        self._socket_address = SocketAddress(ip, port)
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
        print(f'Listening incoming OSC message on port {self.port}')
        msg_count = 0

        while not self.quit_event.is_set():
            self.server.handle_request()
            msg_count += 1
            print(f'msg_count: {msg_count}')

    
    def default_handler(self, address, *args):
        print(f'Default handler called with {address} {args}')