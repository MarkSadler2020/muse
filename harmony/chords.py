import re
from collections import defaultdict
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from muse.patterns import (
    Intervals, LETTERS, LETTERS_REVERSE, 
    SCALES, ACCIDENTALS, ACCIDENTALS_BY_VALUE,
    CHORD_QUALITIES
)

def OR_string(data):
    OR_string = ''
    for i, key in enumerate(data.keys()):
        OR_string += key.upper() + '|' + key.lower()
        if i < len(data) - 1:
            OR_string += '|'
    return OR_string

class Chord():
    """
    Container for an arbitrary collection of notes.
    """
    def __init__(self, name=None, notes=[], scale=None):
        self.notes = notes
        self.scale = []
        self.functional_notes = []

    def stack_thirds(self):
        """
        Return dict of notes where the key is the
        degree that the note contributes to the chord spelling.
        """
        
    def parse_name(self):
        """
        """
        
    def __analyze__(self):
        """
        """


class HarmonyABC(metaclass=ABCMeta):
    """
    Represents a harmonic function, used for harmonic 
    analysis and generation.
    """
    def __init__(self, name, notes=[], scale=None, post_process_name=True):
        self.name = name
        self.name_data = self.parse_name(name)
        self.notes = notes
        self.scale = scale
        self.post_process_name = post_process_name

    @abstractmethod
    def post_process(self):
        """
        """
    
    @abstractmethod
    def build_chord(self):
        """
        """

    @property
    def name(self):
        name_data = self.clean(self.name_data)
        if self.post_process_name:
            name_data = self.post_process(name_data)
        return self.name_format.format(**name_data)

    def clean(self, name_dict):
        """
        Replace None objects with empty strings. Called prior to forming the `name` string.
        """
        for k, v in name_dict.items():
            if not v:
                name_dict[k] = ''
        return name_dict
    
    @property
    @abstractmethod
    def name_format(self):
        return "{letter}{accidental}{quality}{ext_quality}{extension}{modifier1}{modified_degree1}{modifier2}{modified_degree2}{sus}{sus_degree}{add}{add_degree_modifier}{add_degree}"

    @name.setter
    def name(self, value):
        self.parse_name(value)

    @abstractmethod
    def parse_name(self, name):
        """
        Must return a dict
        """
        return dict()

    @property
    def letter(self):
        return self.name_data['letter'].upper()
    
    @property 
    def accidental(self):
        return self.name_data['accidental']
    
    @property 
    def quality(self):
        return self.name_data['quality']

    @property 
    def ext_quality(self):
        return self.name_data['ext_quality']

    @property 
    def extension(self):
        return int(self.name_data['extension'])

    @property 
    def modifier1(self):
        return self.name_data['modifier1']

    @property 
    def modifier1_degree(self):
        return self.name_data['modifier1_degree']

    @property 
    def modifier2(self):
        return self.name_data['modifier2']

    @property 
    def modifier2_degree(self):
        return self.name_data['modifier2_degree']

    @property 
    def sus(self):
        return self.name_data['sus']

    @property 
    def sus_degree(self):
        return self.name_data['sus_degree']

    @property 
    def add(self):
        return self.name_data['add']
    
    @property 
    def add_degree_modifier(self):
        return self.name_data['add_degree_modifier']

    @property 
    def add_degree(self):
        return self.name_data['add_degree']


class Harmony(HarmonyABC):
   
    @property
    def name_format(self):
        return (
            "{letter}{accidental}{quality}{ext_quality}{extension}"
            "{modifier1}{modified_degree1}"
            "{modifier2}{modified_degree2}"
            "{sus}{sus_degree}"
            "{add}{add_degree_modifier}{add_degree}"
        )

    def parse_name(self, name):
        """
        Must return a dict
        """
        reg_str = (
            r'(?P<letter>[{letter}])'
            r'(?P<accidental>[{accidental}]*)?'
            r'(?P<quality>[{quality}])?'
            r'(?P<ext_quality>[{ext_quality}])?'
            r'(?P<extension>{extension}*)?'
            r'(?P<modifier1>{modifier1}*)?'
            r'(?P<modified_degree1>{modified_degree1}*)?'
            r'(?P<modifier2>{modifier2}*)?'
            r'(?P<modified_degree2>{modified_degree2}*)?'
            r'(?P<sus>{sus}*)?'
            r'(?P<sus_degree>{sus_degree})?'
            r'(?P<add>{add}*)?'
            r'(?P<add_degree_modifier>{add_degree_modifier}*)?'
            r'(?P<add_degree>{add_degree})?'
        )

        data = {
            'letter': OR_string(LETTERS),
            'accidental': OR_string(ACCIDENTALS),
            'quality': OR_string(CHORD_QUALITIES),
            'ext_quality': OR_string(CHORD_QUALITIES),
            'extension': OR_string(Intervals),
            'modifier1': OR_string(ACCIDENTALS),
            'modified_degree1': r'[1-9]?[1-9][1-9]',
            'modifier2': OR_string(ACCIDENTALS),
            'modified_degree2': r'[1-9]?[1-9][1-9]',
            'sus': r'sus',
            'sus_degree': r'[1-9]?[1-9][1-9]',
            'add': r'add',
            'add_degree_modifier': OR_string(ACCIDENTALS),
            'add_degree': r'[1-9]?[1-9]?[1-9]'
            }
        
        reg_str = reg_str.format(**data)
        parsed = re.search(reg_str, name)
        parsed_dict = parsed.groupdict()
        if not parsed['ext_quality']:
            parsed_dict.update({'ext_quality': parsed['quality']})

        return parsed_dict
    
    
    def name_abbreviate(self, name_data):
        if name_data['quality'] == name_data['ext_quality']:
            name_data['ext_quality'] = ''
        return name_data

    def name_process(self, name_data):
        abbreviated_name_data = self.name_abbreviate(name_data)
        return abbreviated_name_data
    
    def build(self):
        pass
