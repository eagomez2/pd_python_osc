import sys
import os
import random
import threading
import time
import numpy as np
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))
from apscheduler.schedulers.background import BackgroundScheduler
import ex04_osc as osc

class Note:
    def __init__(self, pitch=69, velocity=64, duration=1000):
        self.pitch = pitch
        self.velocity = velocity
        self.duration = duration

    @property
    def as_osc(self):
        return('/note', [self.pitch, self.velocity, self.duration])
    
    @property
    def as_list(self):
        return([self.pitch, self.velocity, self.duration])


class NoteGenerator(threading.Thread):
    def __init__(self, pitch_range=(48, 48 + 24), velocity_range=(0, 127), duration_range=(10, 1000),
                bpm=120, ppq=448, quantize=False, humanize=False, params={}):
        super().__init__()
        self.setDaemon(True)  # Set thread as daemon

        self.pitch_range = pitch_range
        self.velocity_range = velocity_range
        self.duration_range = duration_range
        self.bpm = bpm
        self.ppq = ppq
        self.params = params
        self.quantize = quantize  # Added for optional quantization of notes
        self.humanize = humanize

    @property
    def tick_duration(self):
        return 60000 / (self.bpm * self.ppq)

    # Property added to facilitate time quantization of notes based on self.quantize value
    @property
    def bpm_duration(self):
        return 60000 / self.bpm

    def fit_to_scale(self):
        pass

    def get_humanized_delta(self, max_variation='32th'):
        # Other max_variation values have not been implemented
        delta = 0

        if max_variation == '32th':
             demisemiquaver = self.bpm_duration / 8.0
             delta += np.random.normal(0, demisemiquaver / 3.0)

             # To avoid the unlikely chance of falling outside 3 * stdev
             delta = np.clip(delta, a_min=-1.0 * demisemiquaver, a_max=demisemiquaver)

        return delta


    def run(self):
        print('Note generator started!\n')
        while not self.params['quit_event'].is_set():
            # Takes the event over if set = True, otherwise wait
            self.params['generate_thread_event'].wait()
            self.params['generate_thread_event'].clear()

            start_time = datetime.now() + \
                         timedelta(seconds=self.params['grace_time_before_playback'])


            for idx in range(self.params['sequence_length']):
                #print(f'Generating note n={idx}:')
                pitch = int(random.randrange(*self.pitch_range))
                velocity = int(random.randrange(*self.velocity_range))
                duration = int(random.randrange(*self.duration_range))

                # If quantize is True, notes are quantized to a 16th notes grid
                if self.quantize:
                    start_time = start_time + timedelta(milliseconds=(self.bpm_duration / 4.0))
                else:
                    if self.params['onset_difference_range'][0] == self.params['onset_difference_range'][1]:
                        start_time = start_time + timedelta(milliseconds=self.params['onset_difference_range'][0])
                    else:
                        start_time = start_time + timedelta(milliseconds=int(random.randrange(*self.params['onset_difference_range'])))

                if self.humanize:
                    humanized_delta = self.get_humanized_delta()
                    humanized_start_time = start_time + timedelta(milliseconds=humanized_delta)
                    scheduled_note = (humanized_start_time, *Note(pitch, velocity, duration).as_list)
                else:
                    scheduled_note = (start_time, *Note(pitch, velocity, duration).as_list)

                self.params['playback_sequence_queue'].put(scheduled_note)
                time.sleep(self.params['generation_time'])
                
                if self.humanize:
                    print(f'n: {idx:02d} pitch: {scheduled_note[1]} velocity: {scheduled_note[2]} duration: {scheduled_note[3]}ms delta:{int(humanized_delta)}ms schedule: {scheduled_note[0].time()}')
                else:
                    print(f'n: {idx:02d} pitch: {scheduled_note[1]} velocity: {scheduled_note[2]} duration: {scheduled_note[3]}ms schedule: {scheduled_note[0].time()}')


class NoteSequenceQueueToPlaybackScheduler(threading.Thread):
    def __init__(self, note_sequence_queue=None, quit_event=None, params={}):
        super().__init__()
        self.setDaemon(True)
        self.note_sequence_queue = note_sequence_queue
        self.params = params
        self.quit_event = quit_event
        self.osc_sender = osc.OSCSender(**params)  # Beware!
        self.playback_scheduler = BackgroundScheduler(daemon=True)
        self.playback_scheduler.start()
    

    def run(self):
        while True:
            note = self.note_sequence_queue.get()

            note = [*note]  # Convert tuple to list to extract pitch, velocity and duration

            start_time = note[0]
            note_args = [note[1:]]

            self.playback_scheduler.add_job(
                self.job_handler,
                'date',
                run_date=start_time,
                args=note_args
            )
    
    
    def job_handler(self, args):
        self.osc_sender.send('/note', args)
        print(f'[{datetime.now().time()}] sending note: {args}')