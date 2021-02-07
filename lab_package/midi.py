import random

class Note:
    def __init__(self, pitch=69, velocity=64, duration=1000):
        self.pitch = pitch
        self.velocity = velocity
        self.duration = duration

    @property
    def as_osc(self):
        return('/note', [self.pitch, self.velocity, self.duration])


class NoteGenerator:
    def __init__(self, pitch_range=(48, 48 + 24), velocity_range=(0, 127), duration_range=(10, 1000)):
        self.pitch_range = pitch_range
        self.velocity_range = velocity_range
        self.duration_range = duration_range
    

    def generate(self, n_samples=1):
        
        notes = []

        for _ in range(n_samples):
            velocity = int(random.randrange(*self.velocity_range))
            duration = int(random.randrange(*self.duration_range))
            pitch = int(random.randrange(*self.pitch_range))

            notes.append(Note(pitch, velocity, duration))
        
        return notes