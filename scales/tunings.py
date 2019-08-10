import math
from collections import namedtuple
from itertools import cycle
import abc
from muse.scales import temperaments

class PitchRangeException(Exception):
    """Raise for note frequencies not between 20-20000"""

class Pitch:
    """
    A value type representing pitch values.

    To-do:
        - Implement operators
    """
    def __init__(self, frequency):
        if frequency < 20 or frequency > 20000:
            message = (
                "Pitch frequency out of range. Allowable values are integers"
                " between 20-20000."
            )
            raise PitchRangeException(message)
        else:
            self.frequency = frequency

    def __eq__(self, value):
        return self.frequency == value

    def __repr__(self):
        return "{frequency} hz".format(frequency=self.frequency)

class TuningABC(metaclass=abc.ABCMeta):
    """
    Abstract base class for tunings.
    """
    def __init__(self, temperament=None, ref_name='A4',
                 ref_freq=440, start_idx=0,stop_idx=49, 
                 step=1, round_precision=2):
        self.counter = 0
        self.round = round_precision
        self.temperament = temperament
        self.tones_per_octave = temperament.tones_per_octave
        self.ref_name = ref_name
        self.ref_freq = ref_freq
        self.dispersion = temperament.dispersion
        self.step = step
        self.start_idx = start_idx
        self.stop_idx = stop_idx

    @abc.abstractmethod
    def step_forward(self):
        """
        """

    @abc.abstractmethod
    def step_backward(self):
        """
        """

    def __call__(self, start=None, stop=None, step=None):
        if not start:
            start = self.start_idx
        if not stop:
            stop = self.stop_idx
        if not step:
            step = self.step

        tuning = type(self)
    
        return tuning(ref_freq=self.ref_freq, ref_name=self.ref_name, start_idx=start, stop_idx=stop,
                      step=step, round_precision=self.round)

    def __iter__(self):
        return self
    
    def __next__(self):
        iteration_length = abs((self.stop_idx - self.start_idx) / self.step)
        while self.counter < iteration_length:
            if self.counter == 0 and self.start_idx == 0:
                frequency = round(self.ref_freq, self.round)
            elif self.step > 0 and self.stop_idx > self.start_idx:
                frequency = self.step_forward()
            elif self.step < 0:
                frequency = self.step_backward()
            else:
                raise StopIteration
            try:
                pitch = Pitch(frequency)
            except PitchRangeException:
                raise StopIteration
            self.counter += 1
            return pitch
        else:
            raise StopIteration

class JustTuning(TuningABC):
    """

    """
    def __init__(self, pattern='pythagorean', *args, **kwargs):
        temperament = temperaments.Just(pattern)
        super().__init__(temperament=temperament, *args, **kwargs)
        if self.step > 0:
            self.temperament.pattern.insert(len(self.temperament.pattern), 1)
        elif self.step < 0:
            self.temperament.pattern.insert(0, 1)

    def next_dispersion(self):
        counter = 0
        while counter < abs(self.step):
            dispersion = next(self.temperament.iterator)
            counter += 1
        octave_factor = self.counter // self.tones_per_octave
        self.dispersion = dispersion * (2 ** octave_factor)

    def step_forward(self):
        """
        Step forward.
        """
        self.next_dispersion()
        # Handle starting index greater than 0. Ex: Tuning(2, ...)
        if self.start_idx >= 0 and self.counter == 0:
            frequency = self.ref_freq * self.dispersion ** (self.start_idx)
        elif self.counter > 0:
            frequency = self.ref_freq * self.dispersion ** self.step
        else:
            frequency = self.ref_freq * self.dispersion
        return round(frequency, self.round)

    def step_backward(self):
        """
        Step backward.
        """
        self.next_dispersion()
        # Handle starting index greater than 0. Ex: Tuning(2, ...)
        if self.start_idx <= 0 and self.counter == 0:
            frequency = self.ref_freq / self.dispersion ** ((self.start_idx) * -1)
        elif self.counter > 0:
            frequency = self.ref_freq / self.dispersion ** (self.step * -1)
        else:
            frequency = self.ref_freq / self.dispersion
        return round(frequency, self.round)

class EqualTuning(TuningABC):
    """
    A callable object which returns an iterator which generates Pitch objects, 
    each of which represents the pitch of a single note in a Scale.

    To-do:
        - Implement __reversed__
        - swap floats for double precision decimals internally.
        - Add some representation of cents, as it is a common expression of pitch.
          Possibly just an offset parameter for the __init__ function.
    """
    def __init__(self, tones_per_octave=12, *args, **kwargs):
        temperament = temperaments.Equal(tones_per_octave)
        super().__init__(temperament=temperament, *args, **kwargs)

    def step_forward(self):
        """
        Step forward.
        """
        # Handle starting index greater than 0. Ex: Tuning(2, ...)
        if self.counter == 0:
            frequency = self.ref_freq * self.dispersion ** self.start_idx
        elif self.counter > 0:
            frequency = self.ref_freq * self.dispersion ** self.step
        else:
            frequency = self.ref_freq * self.dispersion
        # Update ref_freq
        self.ref_freq = frequency
        return round(frequency, self.round)

    def step_backward(self):
        """
        Step backward.
        """
        # Handle starting index greater than 0. Ex: Tuning(2, ...)
        if self.counter == 0:
            frequency = self.ref_freq / self.dispersion ** (self.start_idx * -1)
        elif self.counter > 0:
            frequency = self.ref_freq / self.dispersion ** (self.step * -1)
        else:
            frequency = self.ref_freq / self.dispersion

        # Update ref_freq
        self.ref_freq = frequency
        return round(frequency, self.round)

