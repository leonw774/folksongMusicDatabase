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
    # single
    [n+'1' for n in NOTE_NAME],
    # major third
    [n+'3' for n in NOTE_NAME],
    # minor third
    [n+'m3' for n in NOTE_NAME],
    # major triad
    [n for n in NOTE_NAME],
    # minor triad
    [n+'m' for n in NOTE_NAME],
    # major seven
    [n+'M7' for n in NOTE_NAME],
    # minor seven
    [n+'m7' for n in NOTE_NAME],
    # domin seven
    [n+'7' for n in NOTE_NAME],
]


OLD_CHORD_NOTATION = [
    # single
    ['C1', 'X', 'D1', 'X', 'E1', 'F1', 'X', 'G1', 'X', 'A1', 'X', 'B1'],
    # third
    ['C2', 'X', 'D2', 'X', 'E2', 'F2', 'X', 'G2', 'X', 'A2', 'X', 'B2'],
    # triad
    ['C', 'X', 'Dm', 'X', 'Em', 'F', 'X', 'G', 'X', 'Am', 'X', 'Bo'],
    # seventh
    ['CM7', 'X', 'Dm7', 'X', 'Em7', 'F7', 'X', 'G7', 'X', 'Am7', 'X', 'X']
]


def chord_to_str(c: Chord, is_old=False) -> str:
    return OLD_CHORD_NOTATION[c[0]][c[1]] if is_old else CHORD_NOTATION[c[0]][c[1]]

def chord_seq_to_str(cs: Sequence[Chord], is_old=False) -> str:
    return (
        ','.join([OLD_CHORD_NOTATION[c[0]][c[1]] for c in cs])
        if is_old else
        ','.join([CHORD_NOTATION[c[0]][c[1]] for c in cs])
    )

MusicKey = namedtuple('MusicKey', ['scale_type', 'tonic'])

SCALE_TYPE_NAME = [
    'major',
    'natural minor',
    'harmonic minor',
    'melodic minor'
]
