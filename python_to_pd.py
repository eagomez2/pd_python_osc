import time
import random
from lab_package import midi, osc

if __name__ == '__main__':
    sender = osc.OSCSender(ip='127.0.0.1', port=8888)
    print(f'Instantiated OSC sender to {sender.ip}@{sender.port}')

    note_generator = midi.NoteGenerator(pitch_range=(48, 48 + 24),
                                        velocity_range=(20, 90),
                                        duration_range=(110, 2000))
    
    notes = note_generator.generate(n_samples=32)

    for note in notes:
        sender.send(*note.as_osc)
        time.sleep(random.randrange(1, 10) / 30)