from muse.durations.durations import Duration
from muse.scales.tunings import Pitch, PitchRangeException
from muse.patterns import ACCIDENTALS, ACCIDENTALS_BY_VALUE
from collections import namedtuple, defaultdict
import re

class Note:
    """
    """
    def __init__(self, name='A4', pitch=440, duration=1, scale=None):
        self.scale = scale

        self.name = name
        self.pitch = pitch
        self.duration = duration

    @property
    def accidental_OR_string(self):
        # '#|b|+|-'
        accidental_OR_string = ''
        for i, accidental in enumerate(ACCIDENTALS.keys()):
            accidental_OR_string += accidental
            if i < len(ACCIDENTALS) - 1:
                accidental_OR_string += '|'
        return accidental_OR_string

    def parse_name(self, name):
        reg_str = r'(?P<letter>[A-Ga-g])(?P<accidentals>[{acc}]*)(?P<octave>[\d+]*)?'
        reg_str = reg_str.format(acc=self.accidental_OR_string)
        parsed = re.search(reg_str, name)
        self.letter = parsed.group('letter').upper()
        self.accidentals = parsed.group('accidentals')
        self.octave = parsed.group('octave')

    @property
    def octave(self):
        try:
            return self._octave
        except:
            return None

    @octave.setter
    def octave(self, value):
        try:
            self._octave = int(value)
        except ValueError:
            return None

    @property
    def name(self):
        return self.letter + self.accidentals

    @name.setter
    def name(self, value):
        self.parse_name(value)

    @property
    def letter(self):
        return self._letter

    @letter.setter
    def letter(self, value):
        self._letter = value

    @property
    def accidentals(self):
        if self._accidentals:
            return self._accidentals
        else:
            return ''

    @accidentals.setter
    def accidentals(self, value):
        if not value:
            self._accidentals = ''
        else:
            for accidental in value:
                if not accidental in ACCIDENTALS.keys():
                    msg = "No accidental named '{value}' definied."
                    raise ValueError(msg.format(value=value))
        # This assignment will not occur if any character of value is
        # not in scale.ACCIDENTAL.values()
        self._accidentals = value

    @property
    def accidental_offset(self):
        return sum([ACCIDENTALS[acc] for acc in self.accidentals])

    @property
    def pitch(self):
        """
        Integer representing the note pitch in Hz.
        """
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        """
        Note frequencies limited to human hearing range (20-20000).
        """
        self._pitch = Pitch(value)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = Duration(value)

    def __repr__(self):
        octave = self.octave
        if not self.octave:
            octave = ''
        return self.name + str(octave)
    
    def __eq__(self, value):
        return self.pitch == value.pitch
