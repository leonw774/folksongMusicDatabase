from typing import List

from musical_things import MusicNote, Metre

JIANPU_NUMBER_TO_PITCH = [-1, 0, 2, 4, 5, 7, 9, 11] # index 0 is rest
JIANPU_PREFIXES = set(['+', '-'])
JIANPU_NOTES = set(['0', '1', '2', '3', '4', '5', '6', '7', '^', 'x'])
JIANPU_SEPERATORS = set(['|', '(', ')'])
JIANPU_SUFFIXES = set(['#', 'b', '_', '.'])

JIANPU_PREFFIX_STATE = 0
JIANPU_NOTE_STATE = 1
JIANPU_SUFFIX_STATE = 2
JIANPU_SEPERATOR_STATE = 3

PITCH_TO_JIANPU_NUMBER = [
    ['1'],
    ['1#', '2b'],
    ['2'],
    ['2#', '3b'],
    ['3'],
    ['4'],
    ['4#', '5b'],
    ['5'],
    ['5#', '6b'],
    ['6'],
    ['6#', '7b'],
    ['7b'],
]

def jianpu_to_note_seq(melody_str: str, time_unit: int, metre: Metre) -> List[MusicNote]:
    note_seq: List[MusicNote] = []
    measure_number = 1
    octave = 0
    is_triplet = False
    is_rest = False
    duration = 0
    cur_state = JIANPU_SEPERATOR_STATE
    cur_time = 0

    for c in melody_str:
        if c in JIANPU_SEPERATORS:
            octave = 0
            is_rest = False
            duration = 0
            assert cur_state != JIANPU_PREFFIX_STATE
            if c == '(':
                assert not is_triplet
                is_triplet = True
            elif c == ')':
                assert is_triplet
                is_triplet = False
            elif c == '|':
                if measure_number == 1:
                    assert len(note_seq) > 0, 'Empty first measure'
                    last_note_end = note_seq[-1].end
                    measure_length = int(metre[0] * 4 / metre[1])
                    if cur_time != measure_length:
                        # is anacrusis
                        # print('anacrusis', cur_time, measure_length)
                        right_shift = measure_length - cur_time
                        note_seq = [
                            MusicNote(n.start+right_shift, n.end+right_shift, n.pitch)
                            for n in note_seq
                        ]
                measure_number += 1
            cur_state = JIANPU_SEPERATOR_STATE

        elif c in JIANPU_PREFIXES:
            is_rest = False
            duration = 0
            if c == '+':
                octave += 1
            elif c == '-':
                octave -= 1
            cur_state = JIANPU_PREFFIX_STATE

        elif c in JIANPU_NOTES:
            duration = time_unit * 2 / 3 if is_triplet else time_unit
            if c == '0':
                is_rest = True
            elif c == '^':
                assert len(note_seq) > 0, 'No note before tie'
                if is_triplet:
                    note_seq[-1].end += duration
                else:
                    note_seq[-1].end += duration
            elif c == 'x': # clip or drum
                pass
            else:
                last_note_end = 0
                if len(note_seq) > 0:
                    last_note_end = note_seq[-1].end
                new_note = MusicNote(
                    last_note_end,
                    last_note_end+duration,
                    JIANPU_NUMBER_TO_PITCH[int(c)] + 12 * octave
                )
                note_seq.append(new_note)
            cur_time += duration
            cur_state = JIANPU_NOTE_STATE

        elif c in JIANPU_SUFFIXES:
            assert cur_state == JIANPU_NOTE_STATE or cur_state == JIANPU_SUFFIX_STATE
            octave = 0
            assert len(note_seq) > 0 or is_rest, 'No note before suffix'
            if c == '#':
                note_seq[-1].pitch += 1
            elif c == 'b':
                note_seq[-1].pitch -= 1
            elif c == '_':
                cur_time += duration
                duration *= 2
                if not is_rest:
                    note_seq[-1].end = note_seq[-1].start + duration
            else: # c == '.'
                cur_time += duration / 2
                duration += duration / 2
                if not is_rest:
                    note_seq[-1].end = note_seq[-1].start + duration
            cur_state = JIANPU_SUFFIX_STATE

        else:
            raise ValueError(f'unrecognized character: {c}')
    # end for c in melody_str
    return note_seq

def note_seq_to_jianpu(note_seq: List[MusicNote], time_unit: int, metre: Metre):
    raise NotImplementedError()
