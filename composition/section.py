from muse.durations.durations import Duration, Tuple
from muse.meter.time_signatures import TimeSignature
from copy import deepcopy

class Section():
    def __init__(self, time_signature, key_signature,
                 tempo, music_data, parent_section=None,
                 child_sections=[]):

        self.time_signature = time_signature
        self.key_signature = key_signature
        self.tempo = tempo
        self.music_data = [self.add_note(note) for note in music_data]
        self.parent_section = parent_section
        self.child_sections = child_sections
        self.subdivision_resolution = 128

    def add_note(self, note):
        if isinstance(note, Note):
            note.subsection = self
            return note

    def measure(self, measure_num):
        subdivision_resolution = self.subdivision_resolution
        beats_per_measure = self.time_signature.beats_per_measure
        division_of_beat = self.time_signature.division_of_beat

        start_beat_number = (
            (measure_num * beats_per_measure) - (beats_per_measure - 1)
        )

        # end_beat_number = (end_measure_num * beats_per_measure)

        # Instantiate the measure list and the counter for the cumulative
        # duration of beats.
        measure = []

        subdivisions_per_measure = (
            beats_per_measure * subdivision_resolution / (division_of_beat / 4)
        )

        print(subdivisions_per_measure)
        cumulative_duration = Duration(0, 1, subdivision_resolution)
        for note in self.music_data[start_beat_number - 1:]:
            print(note.duration)
            cumulative_duration += note.duration
            print(cumulative_duration)
            # If the cumulative duration does not exceed the number of
            # allowable beats in a measure, add the note to measure.
            if cumulative_duration <= subdivisions_per_measure:
                measure.append(note)
            # If the cumulative duration does exceed the number of allowable
            # beats in a measure:
            elif (cumulative_duration > beats_per_measure and
                  note.start_beat < (start_beat_number + beats_per_measure)):

                shortened_note = deepcopy(note)

                shortened_note.duration = (
                    note.duration - (cumulative_duration - beats_per_measure)
                )

                shortened_note._is_tied = True
                measure.append(shortened_note)
                break

        return measure

    def measures(self, start_num, end_num):
        measures = []
        for measure_num in range(start_num, end_num + 1):
            measure = self.measure(measure_num)
            measures.append(measure)
        return measures

    def __getitem__(self, value):
        return self.music_data[value]

    def __repr__(self):
        return str(self.music_data)

    def __str__(self):
        return str(self.music_data)
