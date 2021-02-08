import time
import random
from collections import namedtuple
from pythonosc.udp_client import SimpleUDPClient

SocketAddress = namedtuple('SocketAddress', ['ip', 'port'])

class OSCSender:
    """ Class for sending OSC messages from python to Pd.

    This class establishes a connection with Pd server on ip address and port.
    """

    def __init__(self, ip='127.0.0.1', port=8888):
        super().__init__()
        self._socket_address = SocketAddress(ip, port)
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
    
    
    def send(self, address, value):
        self.client.send_message(address, value)