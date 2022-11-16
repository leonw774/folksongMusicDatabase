from collections import namedtuple
from typing import Tuple, Sequence

NOTE_NAME_TO_NUMBER = {
    'C': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'H': 11
}

NOTE_NAME = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

class MusicNote:
    def __init__(self, start: float, end: float, pitch: int) -> None:
        self.start = start
        self.end = end
        self.pitch = pitch

    def __str__(self):
        return f'MusicNote(start={self.start}, end={self.end}, pitch={self.pitch})'

    def __repr__(self):
        return f'MusicNote(start={self.start}, end={self.end}, pitch={self.pitch})'

# MusicNote = namedtuple('MusicNote', ['start', 'end', 'pitch'])

Metre = Tuple[int, int]

Chord = namedtuple('Chord', ['chord_type', 'root'])

CHORD_NOTATION = [
    # major
    ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B'],
    # minor
    ['Cm', 'C#m/Dbm', 'Dm', 'D#m/Ebm', 'Em', 'Fm', 'F#m/Gbm', 'Gm', 'G#m/Abm', 'Am', 'A#m/Bbm', 'Bm'],
    # augmented
    ['C+', 'C#+/Db+', 'D+', 'D#+/Eb+', 'E+', 'F+', 'F#+/Gb+', 'G+', 'G#+/Ab+', 'A+', 'A#+/Bb+', 'B+'],
    # diminished
    ['Co', 'C#o/Dbo', 'Do', 'D#o/Ebo', 'Eo', 'Fo', 'F#o/Gbo', 'Go', 'G#o/Abo', 'Ao', 'A#o/Bbo', 'Bo']
]

def chord_to_str(c: Chord) -> str:
    return CHORD_NOTATION[c[0]][c[1]]

def chord_seq_to_str(cs: Sequence[Chord]) -> str:
    return ','.join([CHORD_NOTATION[c[0]][c[1]] for c in cs])

MusicKey = namedtuple('MusicKey', ['scale_type', 'tonic'])

SCALE_TYPE_NAME = [
    'major',
    'natural minor',
    'harmonic minor',
    'melodic minor'
]
