import abc
from collections import namedtuple
from itertools import cycle, count
import re
import string
import copy

from muse.scales import tunings, temperaments
from muse.scales.notes import Note, PitchRangeException
from muse.patterns import (
    Intervals, INTERVAL_ALIASES, LETTERS, LETTERS_REVERSE, 
    SCALES, ACCIDENTALS, ACCIDENTALS_BY_VALUE
)

class ScaleABC(metaclass=abc.ABCMeta):
    """
    Abstract base class for scales.
    """
    def __init__(self, start_idx=0, stop_idx=49, step=1, ref_name='A4', ref_pitch=440:
        self.counter = 0
        self.start_idx = start_idx
        self.stop_idx = stop_idx
        self.step_size = step

    @property
    def direction(self):
        if self.step_size > 0:
            direction = 'ascending'
        if self.step_size < 0:
            direction = 'descending'
        return direction

    @abc.abstractmethod
    def step(self):
        """
        """

    def __iter__(self):
        note = Note(self.ref_note)
        ref_scale = [n for n in self]
        return self
    
    def __next__(self):
        target_length = abs((self.stop_idx - self.start_idx) / self.step_size)
        while self.counter < target_length:
            note = self.step()
            self.counter += 1
            return note
        else:
            raise StopIteration


class ChromaticScale(ScaleABC):
    """
    An iterator which generates a chromatic scale.

    ChromaticScale objects are passed to DiatonicScale instances
    as arguments.
    """

    def __init__(self, root='C4', tuning=tunings.EqualTuning(12), 
                 start_idx=0, stop_idx=49, step=1, 
                 octave_increment_letter='C'):

        self.root = Note(name=root)
        if not self.root.octave:
            self.root.octave = 4
        self.scale_length = len(self.expanded_ordered_note_letters)

        self.tuning = tuning(start_idx, stop_idx, step)

        self.counter = 0
        self.start_idx = start_idx
        self.stop_idx = stop_idx
        self.step_size = step
        self.names = cycle(self.get_chromatic_names())
        self.notes_per_octave = self.tuning.tones_per_octave
        self.octaves = count(self.root.octave, self.step_size)
        self.octave = next(self.octaves)
        self.octave_increment_letter = octave_increment_letter

        super().__init__(start_idx=start_idx, stop_idx=stop_idx, step=step)

    def step(self):
        """
        Increment through chromatic note names by step.
        """
        name = next(self.names)
        pitch = next(self.tuning)

        if self.is_enharmonic_equivalent(name, self.octave_increment_letter):
            self.octave = next(self.octaves)
        name = name + str(self.octave)

        try:
            note = Note(name=name, pitch=pitch.frequency, scale=self)
        except PitchRangeException:
            raise StopIteration
        return note


    @property
    def ordered_note_letters(self):
        note_letters = list(LETTERS.keys())
        note = self.root
        root_idx = note_letters.index(note.letter)
        return [*note_letters[root_idx:], *note_letters[:root_idx]]
    
    @property
    def expanded_ordered_note_letters(self):
        expanded = []
        for letter in self.ordered_note_letters:
            expanded.append(letter)
            spacing = LETTERS[letter] - 1
            for _ in range(spacing):
                expanded.append(None)
        return expanded

    def get_letter_index(self, letter):
        """
        Given a letter, return the index in the scale.
        """
        return self.expanded_ordered_note_letters.index(letter)
    
    def get_chromatic_index(self, note):
        """
        Given a note name, return the chromatic index of a zero-based
        array representing one octave.

        Used for calculating enharmonic equivalents.
        """
        root = self.root
        if not isinstance(note, Note):
            note = Note(note)
        
        letter_idx = self.get_letter_index(note.letter)
        root_idx = letter_idx + root.accidental_offset
        name_idx = root_idx + note.accidental_offset 
        return name_idx

    def get_chromatic_name(self, letter, target_idx):
        """
        Given a letter name and a chromatic index,
        return the appropriate spelling of that note name.
        """
        root = self.root
        scale_length = self.scale_length
        # root_idx = self.get_letter_index(root.letter) + root.accidental_offset
        letter_idx = self.get_letter_index(letter)
        ref_idx = letter_idx - root.accidental_offset

        accidental_string = ''
        # Ex: [1, -1] for # and b
        accidental_values_sorted = sorted([acc for acc in ACCIDENTALS.values()], reverse=True)

        while ref_idx != target_idx:
            for acc_value in accidental_values_sorted:
                if target_idx - ref_idx >= scale_length - 1:
                    target_idx = target_idx - scale_length
                elif ref_idx > target_idx and acc_value < 0:
                    ref_idx += acc_value
                    accidental_string += ACCIDENTALS_BY_VALUE.get(acc_value)
                elif ref_idx < target_idx and acc_value > 0:
                    ref_idx += acc_value
                    accidental_string += ACCIDENTALS_BY_VALUE.get(acc_value)

        return letter + accidental_string

    def is_enharmonic_equivalent(self, note_x, note_y):
        if not isinstance(note_x, Note):
            note_x = Note(note_x)
        if not isinstance(note_y, Note):
            note_y = Note(note_y)

        if self.get_chromatic_index(note_x.name) == self.get_chromatic_index(note_y.name):
            return True
        else:
            return False

    def variants(self, note, direction):
        """
        Given a letter name, return a list of all remaining modified
        chromatic variants of a given letter name in the direction of iteration.
        """
        if not isinstance(note, Note):
            note = Note(note)

        variants = []
        letter = note.letter
        quanta = LETTERS[letter]
        variants.append(note)
        step = self.step_size

        if direction == 'ascending':
            quanta = LETTERS[letter] * step
        elif direction == 'descending':
            quanta = LETTERS_REVERSE[letter] * step
        for q in range(note.accidental_offset + step, quanta, step):
            letter = copy.deepcopy(letter)
            name = letter + ACCIDENTALS_BY_VALUE.get(q, '')
            note = Note(name)
            variants.append(note)
        return variants

    def get_chromatic_names(self):
        chromatic_scale = []
        ref_note = self.root.name
        ordered_note_letters = copy.deepcopy(self.ordered_note_letters)
        step = self.step_size
        if self.direction == 'ascending':
            counter = 0
        elif self.direction == 'descending':
            counter = self.scale_length
            ordered_note_letters.reverse()
            ordered_note_letters.insert(0, ordered_note_letters.pop())

        letter_iterator = cycle(ordered_note_letters)
        next(letter_iterator)

        while len(chromatic_scale) < self.scale_length:
            variants = self.variants(ref_note, self.direction)
            for variant in variants:
                if len(chromatic_scale) < self.scale_length:
                    ref_note = self.get_chromatic_name(variant.letter, counter)
                    chromatic_scale.append(ref_note)
                    counter += step
            ref_note = next(letter_iterator)

        return chromatic_scale


    def __call__(self, start=None, stop=None, step=None):
        if not start:
            start = self.start_idx
        if not stop:
            stop = self.stop_idx
        if not step:
            step = self.step_size
        
        scale = type(self)
        return scale(root=self.root.name, tuning=self.tuning, 
                     start_idx=start, stop_idx=stop, step=step)

class DiatonicScale(ScaleABC):
    """
    A diatonic scale.
    """
    def __init__(self, 
                 pattern_name='major',
                 chromatic_scale=ChromaticScale(
                    root='C', 
                    tuning=tunings.EqualTuning(12), 
                    start_idx=0, stop_idx=49, step=1)):

        self.chromatic_scale = chromatic_scale
        self.start_idx = self.chromatic_scale.start_idx
        self.stop_idx = self.chromatic_scale.stop_idx
        self.step_size = self.chromatic_scale.step_size
        self.root = self.chromatic_scale.root
        self.tuning = self.chromatic_scale.tuning
        self.pattern_name = pattern_name
        super().__init__(start_idx=self.start_idx, stop_idx=self.stop_idx, step=self.step_size)
        self.names = cycle(self.get_diatonic_names())

    def step(self):
        """
        Increment through diatonic note names by step.
        """
        name = next(self.names)
        name_idx = self.get_diatonic_names().index(name)
        direction = self.direction
        ascending_pattern = self.ascending_pattern
        descending_pattern = self.descending_pattern
        chromatic_scale = self.chromatic_scale

        if direction == 'ascending':
            pattern = ascending_pattern
            next_interval = pattern[name_idx - 1]
        elif direction == 'descending':
            pattern = descending_pattern
            next_interval = pattern[name_idx]

        next_interval_value = Intervals[next_interval]
    
        counter = 0
        while counter < next_interval_value:
            note = next(chromatic_scale)
            note.name = name
            counter += 1
        return note

    @property
    def notes_per_octave(self):
        if self.direction == 'ascending':
            return len(self.ascending_pattern) + 1
        elif self.direction == 'descending':
            return len(self.descending_pattern) + 1

    @property
    def ascending_pattern(self):
        return SCALES[self.pattern_name][0].split(' ')

    @property
    def descending_pattern(self):
        try:
            pattern = SCALES[self.pattern_name][1].split(' ')
        except:
            pattern = SCALES[self.pattern_name][0].split(' ')
            pattern.reverse()
        return pattern
    
    def get_ascending(self):
        intervals = self.ascending_pattern
        letter_iter = cycle(self.chromatic_scale.ordered_note_letters)
        letter = next(letter_iter)
    
        idx = 0
        ascending = []
        for interval in intervals:
            ascending.append(self.chromatic_scale.get_chromatic_name(letter, idx))
            interval = Intervals[interval]
            letter = next(letter_iter)
            idx += interval
        return ascending
    
    def get_descending(self):
        letters = self.chromatic_scale.ordered_note_letters[::-1]
        letters.insert(0, letters.pop())
        letter_iter = cycle(letters)
        letter = next(letter_iter)
        intervals = self.descending_pattern

        idx = self.chromatic_scale.scale_length
        descending = []
        for interval in intervals:
            descending.append(self.chromatic_scale.get_chromatic_name(letter, idx))
            interval = Intervals[interval]
            letter = next(letter_iter)
            idx -= interval
        return descending

    def get_diatonic_names(self):
        if self.direction == 'ascending':
            return self.get_ascending()
        elif self.direction == 'descending':
            return self.get_descending()

    def __call__(self, start=None, stop=None, step=None):
        if not start:
            start = self.start_idx
        if not stop:
            stop = self.stop_idx
        if not step:
            step = self.step_size

        scale = type(self)

        if hasattr(self, 'chromatic_scale'):
            chromatic_scale = self.chromatic_scale(start=start, stop=stop, step=step)

        return scale(pattern_name=self.pattern_name, 
                     chromatic_scale=chromatic_scale)

    def get_note(name, octave=4):
        if octave == 4:
            start_idx = 0
        elif (octave < 4) or (octave >= 4):
            start_idx = self.scale_length * (octave - 4) 
        
        two_octaves = [note for note in self(start_idx, 26)]

