import time
import threading
from lab_package import osc

if __name__ == '__main__':
    quit_event = threading.Event()  # Used to quit OSCReceiver

    # Define handler for the /clock message
    def clock_msg_handler(address, *args):
        print('Clock received')
        print(f'address: {address} args: {args}')

    address_list = ['/clock*']
    address_handler_list = [clock_msg_handler]

    osc_receiver = osc.OSCReceiver(ip='127.0.0.1', 
                                    port=8889, 
                                    quit_event=quit_event,
                                    address_list=address_list,
                                    address_handler_list=address_handler_list)
    
    osc_receiver.start()

    # Runs the server until the application is interrupted
    osc_receiver.server.serve_forever()