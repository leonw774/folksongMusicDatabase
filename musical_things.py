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
    ['C1', 'C#/Db1', 'D1', 'D#/Eb1', 'E1', 'F1', 'F#/Gb1', 'G1', 'G#/Ab1', 'A1', 'A#/Bb1', 'B1'],
    # major third
    ['C3', 'C#/Db3', 'D3', 'D#/Eb3', 'E3', 'F3', 'F#/Gb3', 'G3', 'G#/Ab3', 'A3', 'A#/Bb3', 'B3'],
    # minor third
    ['Cm3', 'C#/Dbm3', 'Dm3', 'D#/Ebm3', 'Em3', 'Fm3', 'F#/Gbm3', 'Gm3', 'G#/Abm3', 'Am3', 'A#/Bbm3', 'Bm3'],
    # major triad
    ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B'],
    # minor triad
    ['Cm', 'C#m/Dbm', 'Dm', 'D#m/Ebm', 'Em', 'Fm', 'F#m/Gbm', 'Gm', 'G#m/Abm', 'Am', 'A#m/Bbm', 'Bm'],
    # augmented triad
    ['C+', 'C#+/Db+', 'D+', 'D#+/Eb+', 'E+', 'F+', 'F#+/Gb+', 'G+', 'G#+/Ab+', 'A+', 'A#+/Bb+', 'B+'],
    # diminished triad
    ['Co', 'C#o/Dbo', 'Do', 'D#o/Ebo', 'Eo', 'Fo', 'F#o/Gbo', 'Go', 'G#o/Abo', 'Ao', 'A#o/Bbo', 'Bo']
]


OLD_CHORD_NOTES = [
    [[0], [], [2], [], [4], [5], [], [7], [], [9], [], [11]],
    [[0, 4], [], [2, 5], [], [4, 7], [5, 9], [], [7, 11], [], [9, 0], [], [11, 2]],
    [[0, 4, 7], [], [2, 5, 8], [], [4, 7, 11], [5, 9, 0], [], [7, 11, 2], [], [9, 0, 4], [], [11, 2, 5]],
    [[0, 4, 7, 11], [], [2, 5, 8, 0], [], [4, 7, 11, 2], [5, 9, 0, 4], [], [7, 11, 2, 5], [], [9, 0, 4, 7], [], [11, 2, 5, 9]],
]

OLD_CHORD_NOTATION = [
    # single
    ['C1', 'X', 'D1', 'X', 'E1', 'F1', 'X', 'G1', 'X', 'A1', 'X', 'B1'],
    # third
    ['C2', 'X', 'D2', 'X', 'E2', 'F2', 'X', 'G2', 'X', 'A2', 'X', 'B2'],
    # triad
    ['C', 'X', 'Dm', 'X', 'Em', 'F', 'X', 'G', 'X', 'Am', 'X', 'Bo'],
    # seventh
    ['CM7', 'X', 'Dm7', 'X', 'Em7', 'F7', 'X', 'G7', 'X', 'Am7', 'X', 'Bo-7']
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
