import random
import threading

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
                bpm=120, ppq=448, params={}):
        super().__init__()
        self.setDaemon(True)  # Set thread as daemon

        self.pitch_range = pitch_range
        self.velocity_range = velocity_range
        self.duration_range = duration_range
        self.bpm = bpm
        self.ppq = ppq
        self.params = params


    @property
    def tick_duration(self):
        return 60000 / (self.bpm * self.ppq)


    def run(self):
        while not self.params['quit_event'].is_set():
            # Takes the event over if set = True, otherwise wait
            self.params['generate_thread_event'].wait()
            self.params['generate_thread_event'].clear()

            sequence = []
            start_time = 0

            for idx in range(self.params['sequence_length']):
                print(f'Generating note n={idx}')
                pitch = int(random.randrange(*self.pitch_range))
                velocity = int(random.randrange(*self.velocity_range))
                duration = int(random.randrange(*self.duration_range))
                start_time = start_time + int(random.randrange(*self.params['onset_difference_range']))
                start_tick = int(start_time / self.tick_duration)

                scheduled_note = (start_tick, *Note(pitch, velocity, duration).as_list)
                self.params['playback_sequence_queue'].put(scheduled_note)

                time.sleep(self.params['generation_time'])
                print(scheduled_note)