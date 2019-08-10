import itertools
import math
import textwrap
from muse.durations import Duration, Tuplet

class BeatGenerator():
    """
    Generates any possible sequence of beats
    within the constraints of parameters.
    """
    def __init__(self, beat=None, resolution=512, precision=2, 
                 permutations=False):
        self.beat = beat
        self.resolution = resolution
        self.precision = precision
        self.permutations = permutations
        self.cache = cache

    def __call__(self, start=None, stop=None, increment=None, permutations=False, idx=None):
        precision = self.precision
        beat = self.beat
        resolution = self.resolution

        # Ex: [10, 9, 8, 7, 6, ..., 0]
        for i in range(precision, 0, -1):
            # create a generator that yields beat divisions
            # within defined constraints
            beat_div_gen = itertools.combinations_with_replacement(self.beats, i)
            # Build a list of beat durations to test if sum
            beat_divs = []
            for beat_div in beat_div_gen:
                float_beat_div = []
                for b in beat_div:
                    float_beat_div.append(1/b * resolution)
                if sum(float_beat_div) == 1/beat * resolution:
                    beat_divs.append(beat_div)

            if self.permutations:
                for _beat_div in beat_divs:
                    # Super inefficient. Makes tons of duplicates which are removed by set().
                    permutations = {permutation for permutation in itertools.permutations(_beat_div)}
                    for permutation in permutations:
                        yield permutation
            else:
                for beat_div in beat_divs:
                    yield beat_div

    @property
    def beats(self):
        linear_res = int(math.log2(self.resolution))
        beats = [2**x for x in range(linear_res)]
        return beats

    def subdivisions(self):
        """
        Return a list of all possible subdivisions of a given
        beat value, constrained only by the precision of
        smallest allowable note.

        May be used for testing durations.
        """
        precision = self.precision
        beat = self.beat
        resolution = self.resolution

        beat_divisions = {}

        # Ex: [10, 9, 8, 7, 6, ..., 0]
        for i in range(precision, 0, -1):
            # create a generator that yields beat divisions
            # within defined constraints
            beat_div_gen = itertools.combinations_with_replacement(self.beats, i)
            # Build a list of beat durations to test if sum
            beat_divs = []
            for beat_div in beat_div_gen:
                float_beat_div = []
                for b in beat_div:
                    float_beat_div.append(1/b * resolution)
                if sum(float_beat_div) == 1/beat * resolution:
                    beat_divs.append(beat_div)
            

                beat_divisions.update({i: {'combinations': beat_divs}})
                if self.permutations:
                    perm_list = []
                    for beat_div in beat_divs:
                        permutations = {permutation for permutation in itertools.permutations(beat_div)}
                        for permutation in permutations:
                            perm_list.append(permutation)
                        beat_divisions[i].update({'permutations': perm_list})
        return beat_divisions



    def beat_report(self):
        divs = self.subdivisions()
        header = 'Precision: {precision}\n'.format(precision=self.precision)
        subheader = '| {counter} | beats: {len} |\n'
        solid_divider = '{} \n'.format('_' * 79)
        dashed_divider = '{} \n'.format('-' * 79)

        combo_counter = 0
        permutation_counter = 0
        data_string = ""
        for length, categories in divs.items():
            combinations = categories['combinations']
            permutations = categories['permutations']
               
            subh = subheader.format(counter=combo_counter, len=length)
            data_string += subh
            data = "Beat Combinations: {combinations} \n".format(combinations=combinations)
            datawrap = ""
            wrap_list = textwrap.wrap(data, width=79)
            for string in wrap_list:
                datawrap += string
                datawrap += '\n'
        
            data2 = "Permutations: {permutations} \n".format(permutations=permutations)
            data2wrap = ""
            wrap_list = textwrap.wrap(data2, width=79)
            for string in wrap_list:
                data2wrap += string
                data2wrap += '\n'

            data_string += datawrap
            data_string += data2wrap
            data_string += dashed_divider
            combo_counter += len(combinations)
            permutation_counter += len(permutations)
        footer = (
            'Total Combinations: {combos}\n'
            'Total Permutations: {perm}\n'
            ).format(combos=combo_counter, perm=permutation_counter)
        return header + solid_divider + data_string + footer + solid_divider
    
    def __str__(self):
        return self.beat_report()

beat_gen = BeatGenerator(beat=1, resolution=512, precision=4, permutations=True)
