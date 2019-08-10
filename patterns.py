ACCIDENTALS = {
#    '♯' : 1, 
#    '♭' : -1,
    '#' : 1,
    'b' : -1,
#    '`' : 2,
#    '~' : -2
}

ACCIDENTALS_BY_VALUE = {value : key for key, value in ACCIDENTALS.items()}

CHROMATIC_INTERVALS = {
    '1': ('P'),
    '2': ('m', 'M'),
    '3': ('m', 'M'),
    '4': ('P'),
    '5': ('d', 'P'),
    '6': ('m', 'M'),
    '7': ('m', 'M'),
}

INTERVAL_ALIASES = {
    'h' : 1,
    'w' : 2,
    'A4' : 7,
}

CHORD_QUALITIES = {
    'dim': ('m3', 'm3'),
    'min': ('m3', 'M3'),
    'Maj': ('M3', 'm3'),
    'Aug': ('M3', 'M3'),
}

EXTENSION_QUALITIES = {
    'min': 'm3',
    'Maj': 'M3',
}

CHORD_DEGREE_MODIFIERS = {
#    '♯' : 1, 
#    '♭' : -1,
    '#' : 1,
    'b' : -1,
    'sus': 0,
#    '`' : 2,
#    '~' : -2
}

class _Intervals:
    def __init__(self, intervals_by_diatonic_degree):
        self.data = intervals_by_diatonic_degree
    
    @property
    def by_diatonic_degree(self):
        return self.data

    @property
    def by_size(self):
        intervals_by_size = {}
        counter = 0
        for diatonic_degree, quality_tuple in self.data.items():
            for quality in quality_tuple:
                interval_name = quality + str(diatonic_degree)
                counter += 1
                intervals_by_size[interval_name] = counter - 1
        return intervals_by_size

    def values(self):
        return self.data.values()

    def keys(self):
        return self.data.keys()
    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        try:
            return self.by_size[key]
        except KeyError:
            return INTERVAL_ALIASES[key]

Intervals = _Intervals(CHROMATIC_INTERVALS)

LETTERS = {
    'A': 2,
    'B': 1,
    'C': 2,
    'D': 2,
    'E': 1,
    'F': 2,     
    'G': 2,
}

# Same as LETTERS, but for the interval behind a given letter name
# rather than in front of the letter name. Used for building
# descending scales.
LETTERS_REVERSE = {}
for i, key in enumerate(LETTERS.keys()):
    if i != 0:
        LETTERS_REVERSE[key] = list(LETTERS.values())[i - 1]
    else:
        LETTERS_REVERSE[key] = list(LETTERS.values())[len(LETTERS) - 1]

SCALES = {
    'major': ('w w h w w w h', None),
    'natural_minor': ('w h w w h w w', None),
    'harmonic_minor': ('w h w w h m3 h', None),
    'melodic_minor': ('w h w w w w h', 'w w h w w h w'),
}


Accidentals = ACCIDENTALS
AccidentalsByValue = ACCIDENTALS_BY_VALUE
Scales = SCALES
Letters = LETTERS
LettersReverse = LETTERS_REVERSE
Intervals = _Intervals(CHROMATIC_INTERVALS)
IntervalAliases = INTERVAL_ALIASES 
