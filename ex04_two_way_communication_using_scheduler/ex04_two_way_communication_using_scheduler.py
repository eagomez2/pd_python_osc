import sys
import os
import queue
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lab_packages import ex04_midi as midi
from lab_packages import ex04_osc as osc


if __name__ == '__main__':
    ticks_queue = queue.Queue(maxsize=0)
    playback_sequence_queue = queue.Queue(maxsize=0)
    generate_thread_event = threading.Event()
    quit_event = threading.Event()

    print(f'Tasks todo: {playback_sequence_queue.unfinished_tasks}')

    def clock_message_handler(address, *args):
        print(f'estimated ticks_queue size: {ticks_queue.qsize()}')
        ticks_queue.put(args[0])


    def actions_handler(address, *args):
        address = address.split('/actions')[-1]

        if '/generate' in address:
            generate_thread_event.set()
            print('note_generator notified!')

    params = {

    }

    clock_tick_receiver = osc.OSCReceiver(ip='127.0.0.1', port=8888,
                                           quit_event=quit_event,
                                           address_list=['/clock*'],
                                           address_handler_list=[clock_message_handler])


    actions_msg_receiver = osc.OSCReceiver(ip='127.0.0.1', port=8889,
                                                quit_event=quit_event,
                                                address_list=['/actions*'],
                                                address_handler_list=[actions_handler])


    note_generator = midi.NoteGenerator(pitch_range=(40, 52),
                                        velocity_range=(78, 80),
                                        duration_range=(30, 200),
                                        params = {
                                            'generate_thread_event': generate_thread_event,
                                            'playback_sequence_queue': playback_sequence_queue,
                                            'sequence_length': 16,
                                            'generation_time': .1,
                                            'onset_difference_range': (100, 100),
                                            'grace_time_before_playback': 2,
                                            'quit_event': quit_event,
                                        })


    playback_scheduler = midi.NoteSequenceQueueToPlaybackScheduler(
        note_sequence_queue=playback_sequence_queue,
        quit_event=quit_event,
        params = {
            'ip': '127.0.0.1',
            'port': 9000,
            'playback_sequence_queue': playback_sequence_queue,
        }
    )

    

    # Start stuff here
    clock_tick_receiver.start()

    time.sleep(1000)