import queue
import time
import threading
import sys

sys.path.append('..')
from lab_packages import ex03_osc as osc
from lab_packages import ex03_midi as midi


if __name__ == '__main__':

    def clock_message_handler(address, *args):
        # print('received something!')
        ticks_queue.put(args[0])


    def actions_handler(address, *args):
        address = address.split('/actions')[-1]

        if '/generate' in address:
            generate_thread_event.set()  # Green light to generate notes
            print('note_generator notified!')
    

    ticks_queue = queue.Queue(maxsize=0)  # queue = FIFO
    playback_sequence_queue = queue.Queue(maxsize=0)
    generate_thread_event = threading.Event()
    quit_event = threading.Event()

    params = {
    }

    ticks_receiver = osc.OSCReceiver(ip='127.0.0.1', port=8888, quit_event=quit_event,
                                     address_list=['/clock*'],
                                     address_handler_list=[clock_message_handler])

    actions_receiver = osc.OSCReceiver(ip='127.0.0.1', port=8889, quit_event=quit_event,
                                       address_list=['/actions*'],
                                       address_handler_list=[actions_handler])

    note_generator = midi.NoteGenerator(pitch_range=(42, 42 + 24),
                                        velocity_range=(78, 80),
                                        duration_range=(800, 2000),
                                        params = {
                                            'onset_difference_range': (1000, 1001),
                                            'generate_thread_event': generate_thread_event,
                                            'quit_event': quit_event,
                                            'playback_sequence_queue': playback_sequence_queue,
                                            'sequence_length': 16,
                                            'generation_time': .4,
                                        })

    note_sender = osc.OSCSender(ip='127.0.0.1', port=9000, 
                                ticks_queue=ticks_queue, 
                                playback_sequence_queue=playback_sequence_queue)

    ticks_receiver.start()
    actions_receiver.start()
    note_generator.start()
    note_sender.start()

    time.sleep(1000)
    quit_event.set()