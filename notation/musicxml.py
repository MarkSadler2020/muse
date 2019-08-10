from collections import namedtuple

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

# default_template = {
#     'score-partwise': {
#         'work':{
#             'attrs': {},
#             'elements': {'work-title': None, 'work-number': None}, 
#             'data': ""
#         }, 
#         'identification': {
#             'encoding':{
#                 'software': None,
#                 'encoding_date': None,
#                 'supports': [
#                     {'element': 'accidental', 'type': 'yes'},
#                     {'element': 'print', 'attribute': 'new-page', 'type': 'yes', 'value': 'yes'},
#                     {'element': 'print', 'attribute': 'new-system', 'type': 'yes', 'value': 'yes'},
#                     {'element': 'stem', 'type': 'yes'},
#                 ]
#             },
#         },
# 
#     },
# }
# 
# 
# 
# class Part:
#     """
#     """
#     def __init__(self, element):
#         self.element = element
#     
#     def stave(self, stave_number):
#         """
#         """
# 
# class Stave:
#     """
#     """

class Note:
    def __init__(self, element):
        self.element = element

    @property
    def pitch(self):
        if not self.element.find('rest'):
            pitch_element = self.element.find('pitch')
        else:
            pitch_element = self.element.find('rest')
        return pitch_element

    @property
    def letter(self):
        if self.pitch is not None:
            letter = self.pitch.find('step').text
            return letter
        else:
            return None

    @property
    def octave(self):
        if self.pitch is not None:
            octave = self.pitch.find('octave').text
            return octave
        else:
            return None
    
    @property
    def name(self):
        if self.pitch is not None:
            name = self.letter + self.octave
            return name
        else:
            return None

    @property
    def duration(self):
        return self.element.find('duration')
    
    @property
    def duration_type(self):
        return self.element.find('type')

    @property
    def voice(self):
        return self.element.find('voice')

    @property
    def stem(self):
        return self.element.find('stem')
    
    @property
    def staff(self):
        return self.element.find('staff')

class Measure:
    def __init__(self, element):
        self.element = element
    
    @property
    def number(self):
        return self.element.get('number')

    @property
    def notes(self):
        note_elements = self.element.findall('note')
        notes = []
        for element in note_elements:
            note = Note(element) 
            notes.append(note)
        return notes

class Score:
    def __init__(self, tree=None, data=None):
        """
        """
        self.tree = tree

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, value):
        if isinstance(value, etree._ElementTree):
            self._tree = value
        elif isinstance(value, str):
            self.load(value)
        else:
            raise TypeError

    def load(self, source):
        """
        Load XML from string, filename, HTTP or FTP URL, file-like object, or open file object.
        """
        self.tree = etree.parse(source)


    def create_element(self, tag='', attrs=None, data=''):
        tree = etree.TreeBuilder()
        if not attrs:
            attrs = {}
        tree.start(tag, attrs)
        tree.data(data)
        tree.end(tag)
        return tree.close()

    def create_tree(self):
        root = self.create_element('score-partwise', {'version': "3.1"})
        self.tree = etree.ElementTree(root)

    @property
    def parts(self):
        parts = self.tree.getroot().findall('part')
        return parts

    @property
    def part_ids(self):
        part_ids = [x.get('id') for x in self.parts]
        return part_ids

    def get_parts(self, part_ids=None):
        """
        Return an XMLElement for each part for every 
        part id provided in the part_ids list. 
        
        If none are provided, all parts are returned.
        """
        parts = {}
        if not part_ids:
            part_ids = self.part_ids
        for part in self.parts:
            part_id = part.get('id')
            if part_id in part_ids:
                parts[part_id] = part
        return parts

    @property
    def identification(self):
        """
        """
        return self.tree.getroot().find('identification')

    @property
    def defaults(self):
        """
        """
        return self.tree.getroot().find('defaults')

    @property
    def score_parts(self):
        """
        """
        return self.tree.getroot().find('part-list').findall('part')

    @property
    def work(self):
        """
        """
        Work = namedtuple('Work', ['work_number', 'work_title'])
        work = self.tree.getroot().find('work')
        return Work(work.find('work-number'), work.find('work-title'))
    
    @property
    def encoding(self):
        """
        """
        Encoding = namedtuple('Encoding', ['software', 'encoding_date', 'supports'])
        encoding = self.identification.find('encoding')
        return Encoding(encoding.find('software'), encoding.find('encoding-date'), encoding.findall('supports'))

    def measures(self, start=None, end=None, step=1, part=None, parts=None):
        """
        """
        data = {}
        if not parts:
            parts = self.parts

        if not start:
            start = 0
        if not end:
            end = start + 1

        for p in parts:
            if isinstance(p, etree._Element):
                part_id = p.get('id')
            else:
                part_id = p
                p = self.get_part(part_id)
            measure_elements = p.findall('measure')
            if start:
                measure_elements = measure_elements[start:end:step]
            measures = [Measure(element) for element in measure_elements]
            data[part_id] = measures

        if part:
            return data[part]
        else:
            return data
    
    def measure(self, measure_number, part=None, parts=None):
        """
        """
        measures = self.measures(measure_number, part=part, parts=parts)
        if part:
            measures = measures[0]
        else:
            measures = {part_name: measure[0] for part_name, measure in measures.items()}
        return measures

    def get_part(self, part_id):
        """
        """
        return self.get_parts(part_ids=[part_id])[part_id]

    def add_part(self):
        """
        """
        

