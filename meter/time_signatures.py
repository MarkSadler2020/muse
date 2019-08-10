import math

class TimeSignatureError(Exception):
    """
    Raised when an invalid number has been passed to
    an instance of TimeSignature.
    """

class TimeSignature():
    def __init__(self, beats_per_measure, division_of_beat):
        self.beats_per_measure = beats_per_measure
        self.division_of_beat = division_of_beat

    @property
    def beats_per_measure(self):
        return self._beats_per_measure

    @beats_per_measure.setter
    def beats_per_measure(self, value):
        if isinstance(value, int) and value > 0:
            self._beats_per_measure = value
        else:
            raise TimeSignatureError("Beats Per Measure must be \
                                     expressed as a positive integer.")

    @property
    def division_of_beat(self):
        return self._division_of_beat

    @division_of_beat.setter
    def division_of_beat(self, value):
        if math.log2(value) % 1 != 0:
            message = ("Beat must be divided by value equal to \
                       either 1 or 2**x.")
            raise TimeSignatureError(message)
        self._division_of_beat = value

    def __repr__(self):
        values = dict(beats_per_measure=self.beats_per_measure,
                      division_of_beat=self.division_of_beat)
        return "{beats_per_measure} / {division_of_beat}".format(**values)

    def __str__(self):
        kwargs = dict(beats_per_measure=self.beats_per_measure,
                      division_of_beat=self.division_of_beat)

        new_str = "{beats_per_measure} / {division_of_beat}"

        return new_str.format(**kwargs)
