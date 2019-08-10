from itertools import cycle
import copy
class Just:
    """
    """
    patterns = {
        'harmonic':
            [25/24, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8],
        'pythagorean':
            [1024/729, 256/243, 128/81, 32/27, 16/9, 4/3, 1/1, 3/2, 9/8, 
             27/16, 81/64, 243/128, 729/512]
    }
    def __init__(self, pattern, patterns={}):
        self.patterns.update(patterns)
        self.pattern = copy.deepcopy(self.patterns[pattern])
        self.tones_per_octave = len(self.pattern) + 1
        self.dispersion = 0
        self.iterator = cycle(self.pattern)

class Equal:
    """
    """
    def __init__(self, tones_per_octave):
        self.tones_per_octave = tones_per_octave
        self.dispersion = 2 ** (1 / tones_per_octave)