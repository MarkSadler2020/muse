import math
import copy
from fractions import Fraction
import itertools
from collections import namedtuple

SUBDIVISION_SYMBOLS = {
    1: ("whole", "whole", "1/1"),
    2: ("half", "half", "1/2"),
    4: ("quarter", "quarter", "1/4"),
    8: ("eigth", "8th", "1/8"),
    16: ("sixteenth", "16th", "1/16"),
    32: ("thirty second", "32nd", "1/32"),
    64: ("sixty fourth", "64th", "1/64"),
    128: ("one hundred and twenty eight", "128th", "1/128"),
    256: ("two hundred and fifty sixth", "256th", "1/256"),
    512: ("five hundred and twelfth", "1/512"),
}

def beat_dur(value, resolution):
    """Utility function that converts beats to durations 
    and durations to beats.

    Beats and durations are inversions of each other,
    so the same function can transform either type of value 
    in either direction.

    Parameters
	----------
    value : int or float
        Represents either a subdivision of the beat or duration in ticks.

    resolution : int
        Indicates the number of ticks per whole note.

    Returns
	----------
    float
        Value represents either beats or duration, depending on which was passed to it.
    """

    try:
        if is_subdivision(value):
            return (1 / value) * resolution
        else:
            msg = ("Duration.beat_dur(value) received "
                   "invalid groupings for value.")
            raise ValueError(msg)
    except ZeroDivisionError:
        return 0.0

def is_subdivision(beat):
    """Test if `beat` is a valid rhythmic subdivision.

    Parameters
	----------
    beat : int
        A `float` or `int` value to be checked for validity as a beat value.

    Returns
	----------
    bool
        Returns `True` if value is positive power of 2. Returns `False` if 
    """
    if beat == 0:
        # Allow 0 duration values if set via argument.
        return True
    elif math.log2(beat) % 1 == 0 and beat > 0:
        return True
    else:
        return False

def is_grouping(beat_value):
    """
    Test if the beat value is a valid grouping of subdivisions.
    Must be either 0, 1, or an integer which is both positive and even.
    Returns either True or False.
    """
    if beat_value == 0:
        # Allow 0 duration values if set via argument.
        return True
    elif beat_value == 1:
        return True
    elif beat_value % 2 == 0 and beat_value > 0:
        return True
    else:
        return False

def group(value, resolution):
    """
    Break down durations into valid beat subdivisions,
    largest to smallest, with the largest being
    a whole note (1 * resolution).
    """
    if not is_grouping(value):
        msg = "Duration.is_grouping failed with {value}"
        raise GroupingValueError(msg.format(value=value))
    grouping = []
    while value >= 1:
        if value == 0:
            grouping.append(value)
            max_valid = 0.0
        else:
            linear_res = int(math.log2(resolution) + 1)
            valid = [2**x
                     for x in range(0, linear_res)
                     if 2**x <= value]

            max_valid = max(valid)
            grouping.append(max_valid)
            value = value - max_valid
    return grouping

def match_resolution(*args):
    """
    Takes an arbitrary number of Duration objects as arguments,
    returns a list of Duration arguments with the resolution matched
    to the highest resolution of the original durations provided.
    """
    max_res = max([duration.resolution for duration in args])
    matched_durations = []
    for duration in args:
        new_duration = copy.deepcopy(duration)
        new_duration.resolution = max_res
        matched_durations.append(new_duration)
    return matched_durations

class GroupingTypeError(TypeError):
    """
    Raised whenever Duration.group() is given an invalid type
    for grouping.
    """
    pass

class GroupingValueError(ValueError):
    """
    Raised whenever Duration.group() is given an invalid value
    for grouping.
    """
    pass

class BeatTuple:
    """
    A namedtuple which holds the raw beat data for each part of the duration object.
    """
    def __init__(self, value, tuplet=None):
        beat_tuple = namedtuple('BeatTuple', ['value', 'tuplet'])
        self.named_beat_tuple = beat_tuple(value, tuplet)

    @property
    def value(self):
        return self.named_beat_tuple.value
    
    @property
    def tuplet(self):
        return self.named_beat_tuple.tuplet
    
    def __getitem__(self, idx):
        return self.named_beat_tuple[idx]

    def __repr__(self):
        return "({value}, {tuplet})".format(value=self.value, tuplet=self.tuplet)


class BeatArray:
    """
    A container that holds BeatTuples for every Duration object.

    BeatTuples are stored in self.data.

    self.beats[0] will return a Duration object instantiated from the data in self.data.
    """

    def __init__(self, *args, beats=[], duration=None):
        self.duration = duration
        self.data = [*args, *beats]

    def append(self, value):
        if isinstance(value, list):
            beats = self.clean_multiple(value)
            for beat in beats:
                self.data.append(beat) 
        if isinstance(value, (int, float, tuple)):
            value = self.clean_single(value, output=BeatTuple)
            self.data.append(value)
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = self.clean(value)

    @property
    def duration(self):
        return self._duration
 
    @duration.setter
    def duration(self, value):
        if not value:
            self._duration = Duration(beat_array=self)
        else:
            self._duration = value

    @property
    def resolution(self):
        return self.duration.resolution
    
    def clean(self, value):
        if isinstance(value, list):
            return self.clean_multiple(value)
        elif isinstance(value, (int, float, tuple)):
            return self.clean_single(value)

    def clean_single(self, beat, output=BeatTuple):
        """
        This function allows the append() and __setitem__() methods
        to handle input in the form of either a tuple:

        >>> BeatArray((4, '1/1/1'))

        Or int, or float:

        >>> BeatArray(4)
        """
        if isinstance(beat, tuple):
            beat = BeatTuple(beat[0], beat[1])
        elif isinstance(beat, int):
            beat = BeatTuple(beat, str(self.duration.tuplet))
        if is_subdivision(beat.value):
            if output is list:
                return [beat]
            elif output is BeatTuple:
                return beat

        else:
            raise ValueError(
                'Value: {beat}\n'
                'Value is not a valid beat subdivision.'
                'Value must be a positive integer which is a power of 2.'
                '(Example: [2, 4, 8, 16, 32, ...,])'.format(beat=beat.value)
            )

    def clean_multiple(self, beats):
        """
        x = [(4, '1/1/1')]
        x = [4]
        """
        cleaned_list = []
        for beat in beats:
            cleaned_list.append(self.clean_single(beat, output=BeatTuple))
        return cleaned_list

    def __getitem__(self, idx):
        beats, tuplet = self.data[idx]
        return Duration(beats, tuplet=tuplet)

    def __setitem__(self, idx, value):
        if isinstance(value, list):
            value = self.clean_multiple(value)
        if isinstance(value, (int, float, tuple)):
            value = self.clean_single(value)
        
        self.data[idx] = value

    def __repr__(self):
        pretty_list = []
        for beat in self.data:
            if beat[1] == str(self.duration.tuplet):
                pretty_list.append(beat[0])
            else:
                pretty_list.append((beat[0], beat[1]))
        return str(pretty_list)
   
class Duration():
    """
    A class representing musical durations.

    Duration values are stored in self._beats as a BeatArray 
    of two dimensional tuplets, where the first position is a 
    beat value represented by an integer which is a power of 2,
    and the second position is a '/' delimited string
    representing a tuplet ratio.

    Examples
    ---------

    >>> BeatArray((4, '1/1/1'))
    Duration(beats=[4], resolution=512)

    The properties self.beats, self.duration, and self.beat_durations all
    render different views of the BeatArray, and setter methods for
    converting values into musical durations
    ---

    **Ex. 1: Setting Duration.beats**

    >>> d = Duration(beats=[8, 8], resolution=512)
    >>> d
    [8, 8]
    >>> d.duration
    128
    >>> d.beats
    [8, 8]
    >>> d.beat_durations
    [64, 64]
    >>> d.beats = [4, 4, 4]
    >>> d.duration
    384

    **Ex. 2: Setting Duration.duration**

    >>> d = Duration(beats=0, resolution=512)
    >>> d.duration = 1024 # two whole notes
    >>> d.beats
    [1, 1]

    """

    def __init__(self, *args, beats=[], tuplet='1/1/1', beat_array=None,
                 resolution=512, use_durations=False):

        if beats == 0:
            beats = []
        elif beats == [0]:
            beats = []

        # Maintain the order of the following assignment statements
        self.resolution = resolution
        self.tuplet = tuplet
        if beat_array:
            self._beats = beat_array
        else:
            self._beats = BeatArray(beats=[*args, *beats], duration=self)

    @property
    def beats(self):
        return self._beats

    @beats.setter
    def beats(self, value):
        self._beats.data = self.beats.clean_multiple(value)

    @property
    def beat_durations(self):
        """
        This property is an interface for getting/setting beats
        as beat durations, calculated as 1/beat * resolution.

        Data is stored as beats and converted back to durations
        on lookup.

        Data is assigned by passing off to the setter for Duration.beats.
        """
        beats = [
            beat_dur(beat.value, self.resolution) * Tuplet(ratio=beat.tuplet).adjustment_factor
            for beat in self.beats.data
        ]
        return beats

    @beat_durations.setter
    def beat_durations(self, durations):
        if hasattr(durations, '__iter__'):
            beats = []
            for duration in durations:
                duration_group = group(duration, self.resolution)
                beat_group = [
                    (int(beat_dur(duration, self.resolution)), (str(self.tuplet)))
                    for duration in duration_group
                ]
                beats.append(*beat_group)

            self.beats = beats

        elif isinstance(durations,(int, float)):
            grouped_durations = group(durations, self.resolution)
            self.beats = [
                (int(beat_dur(duration, self.resolution)), (str(self.tuplet)))
                for duration in grouped_durations
            ]
        else:
            raise TypeError

    @property
    def duration(self):
        """
        Render and return absolute value of self.beats,
        calculated as sum self.beat_durations.
        """
        return sum(self.beat_durations)

    @duration.setter
    def duration(self, value):
        """
        Sets self.duration indirectly by delegating to the setter for
        self.beat_durations, which converts an int or float value to 
        a valid array of beats to assign self.beats.

        Work is delegated to the beat_durations setter.
        """
        self.beat_durations = value

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        self._resolution = value

    @property
    def tuplet(self):
        return self._tuplet

    @tuplet.setter
    def tuplet(self, value):
        self._tuplet = Tuplet(ratio=value)

    def operand_type_handler(self, value):
        """
        Takes a value, returns a Duration object.
        Used to prepare operands for processing in
        operand overload dunder methods.

        Duration objects are passed through untouched.

        Delegates to the setter for Duration.beats to
        handle ints, floats, tuples, and lists in the 
        initialization of new Duration objects.

        """
        if isinstance(value, Duration):
            duration = value
        else:
            duration = Duration(beats=value, resolution=self.resolution)

        return duration

    def __repr__(self):
        if str(self.tuplet) != '1/1/1':
            repr_str = "Duration(beats={beats}, tuplet={tuplet}, resolution={resolution})"
            return repr_str.format(beats=self.beats, tuplet=self.tuplet, resolution=self.resolution)
        else:
            repr_str = "Duration(beats={beats}, resolution={resolution})"
            return repr_str.format(beats=self.beats, resolution=self.resolution)


    def __add__(self, value):
        """
        """
        # For other types, convert them in appropriate
        # Duration objects for comparison.
        value = self.operand_type_handler(value)
        # A copy of self with the same resolution as value.
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])
        # Borrow the resolution attribute from druation1.
        resolution = duration1.resolution
        self.resolution = resolution

        # Rather than added, the values for beats of both
        # matched duration objects are unpacked into a list
        # to be passed to duration1.beats.
        #
        # This maintains the groupings of note values, as well
        # as their order. Adding takes place the Duration.duration 
        # property, which sums the
        beats = [*duration1.beats.data, 
                *duration2.beats.data]

        return Duration(beats=beats)

    def __radd__(self, value):
        pass

    def __sub__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])
        resolution = duration1.resolution

        duration_difference = duration1.duration - duration2.duration
        beat_durations = group(duration_difference, resolution)

        return Duration(beats=beat_durations,
                        resolution=resolution,
                        use_durations=True)

    def __gt__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])

        return duration1.duration > duration2.duration

    def __lt__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])

        return duration1.duration < duration2.duration

    def __eq__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])

        return duration1.duration == duration2.duration

    def __ge__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])

        return duration1.duration >= duration2.duration

    def __le__(self, value):
        value = self.operand_type_handler(value)
        matched = match_resolution(self, value)
        duration1, duration2 = (matched[0], matched[1])

        return duration1.duration <= duration2.duration

    def __mul__(self, value):
        if not isinstance(value, int) or not isinstance(value, float):
            raise TypeError("Operand must be of type int or type float.")

        resolution = self.resolution
        product = self.duration * value
        beat_durations = group(product, resolution)

        return Duration(beats=beat_durations, resolution=resolution, use_durations=True)

#    def __mod__(self, value):
#        """
#        """
#        # Create a Duration object from ints, lists, and tuples.
#        # Duration objects are passed through unchanged.
#        value = self.operand_type_handler(value)
#        # A copy of self with the same resolution as value.
#        duration = match_resolution(value)
#        duration.duration = duration.duration % value.duration
#        return duration
#
#    def __truediv__(self, value):
#        """
#        """
#        # A copy of self with the same resolution as value.
#        duration = copy.deepcopy(self)
#        duration.duration = duration.duration / value
#        return duration
#

    def __str__(self):
        return str(self.beats)


class Tuplet:
    """
    Tuplet instances are assigned to Duration().tuplet,
    and provide an interface for modifying the duration's
    value by distorting its values across the specified 
    tuplet ratio.
    """
    def __init__(self, ratio=None, subdivision=None, numerator=None, 
                 against=None, resolution=512):

        self.resolution = resolution
        if ratio:
            self.ratio = ratio
        elif numerator and against and subdivision:
            self.numerator = int(numerator)
            self.denominator = int(against)
            self.subdivision = int(subdivision)
        else:
            name = type(self).__name__
            raise TypeError(
                '{name}() missing required positional arguments:\n'
                ' - ratio\n or \n - subdivision, numerator,'
                ' against'.format(name = name)
                )

    @property
    def size(self):
        return (
            beat_dur(value=self.subdivision, resolution=self.resolution) 
            * self.denominator
        )

    @property
    def adjustment_factor(self):
        adjustment_factor = (
            self.size 
            / self.numerator 
            / beat_dur(self.subdivision, self.resolution)
        )

        if self.numerator < self.denominator:
            adjustment_factor = adjustment_factor / 2
        
        return adjustment_factor

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value):
        self._ratio = value
        subdivision, numerator, denominator = value.split('/')
        self.subdivision = int(subdivision)
        self.numerator = int(numerator)
        self.denominator = int(denominator)

    @property
    def subdivision(self):
        return self._subdivision

    @subdivision.setter
    def subdivision(self, value):
        self._subdivision = value

    @property
    def numerator(self):
        return self._numerator

    @numerator.setter
    def numerator(self, value):
        self._numerator = value

    @property
    def denominator(self):
        return self._denominator

    @denominator.setter
    def denominator(self, value):
        self._denominator = value


    @property
    def tuplet_resolution(self):
        return (self.resolution / self.size) * (self.numerator / self.denominator)

    @property
    def parts(self):
        tuplet_parts = [
            self.subdivision,
            self.numerator,
            self.denominator
        ]
        return tuplet_parts

    def __str__(self):
        kwargs = {
            'numerator': self.numerator,
            'denominator': self.denominator,
            'subdivision': self.subdivision,
        }
        return (
            "{subdivision}/{numerator}/{denominator}").format(**kwargs)


    def __repr__(self):
        kwargs = {
            'numerator': self.numerator,
            'denominator': self.denominator,
            'subdivision': self.subdivision,
        }

        return (
            "Tuplet(subdivision={subdivision}"
            " numerator={numerator},"
            " against={denominator})").format(**kwargs)



