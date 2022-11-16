from math import exp
from typing import List

from musical_things import (
    MusicNote, Chord, MusicKey, Metre, chord_to_str
)

# Chord weights
CHORD_MAJOR_W       = [10, -5, -2, -5, 8, -2, -1, 8, -2, -5, -1, -2]
CHORD_MINOR_W       = [10, -5, -2, 8, -5, -1, -2, 8, -5, -2, -1, -2]
CHORD_AUGMENTED_W   = [8, -4, -2, -4, 8, -4, -2, -4, 8, -4, -2, -4]
CHORD_DIMINISH_W    = [8, -4, -4, 8, -4, -4, 8, -4, -4, 0, -4, -4]

CHORD_WEIGHTS = [
    CHORD_MAJOR_W,
    CHORD_MINOR_W,
    CHORD_AUGMENTED_W,
    CHORD_DIMINISH_W
]

SCALE_MAJOR_W           = [10, -10, 10, -10, 10, 10, -8, 10, -10, 10, -8, 10]
SCALE_NATURAL_MINOR_W   = [10, -10, 10, 10, -10, 10, -8, 10, 10, -10, 10, -8]
SCALE_HARMONIC_MINOR_W  = [10, -10, 10, 10, -10, 10, -10, 10, 10, -10, -8, 10]
SCALE_MELODIC_MINOR_W   = [10, -10, 10, 10, -10, 10, -10, 10, 0, 2, 0, 2]

SCALE_WEIGHTS = [
    SCALE_MAJOR_W,
    SCALE_NATURAL_MINOR_W,
    SCALE_HARMONIC_MINOR_W,
    SCALE_MELODIC_MINOR_W,
]

# control how much chord_scale_prob and chord_window_prob contribute to the final score
# window_score = (chord_scale_prob ** ALPHA) * (chord_window_prob ** BETA)
ALPHA = 0.3
BETA = 1.0

# use higher temperature to prevent one chord get all the probability
SCALE_TEMPERATURE = 12.0
NEG_MAX = float('-inf')


def argmax(x):
    return max(range(len(x)), key=lambda i: x[i])

def softmax(x, temperature=1.0):
    x = [i / temperature for i in x]
    e_x = list(map(exp, x))
    sum_e_x = sum(e_x)
    return [i / sum_e_x for i in e_x]

def quartile_three(x):
    s = sorted(x)
    k = 3 * len(s) // 4
    if len(s) % 4 < 2:
        return (s[k-1] + s[k]) / 2
    else:
        return s[k-1]

def mean(x):
    return sum(x) / len(x)


def denormalize_note_seq(note_seq: List[MusicNote], tonic: int):
    assert 0 <= tonic < 12
    normalized_note_seq = [
        MusicNote(n.start, n.end, n.pitch+tonic)
        for n in note_seq
    ]
    return normalized_note_seq


def normalized_note_seq_to_scale_type(normalized_note_seq: List[MusicNote]) -> int:
    full_seq_profile = [0] * 12
    for n in normalized_note_seq:
        note_duration = n.end - n.start
        pitch_class = n.pitch
        if pitch_class < 0:
            pitch_class += (pitch_class // 12) * 12
        pitch_class = pitch_class % 12
        full_seq_profile[pitch_class] += note_duration
    scale_scores = [
        sum([a * b for a, b in zip(full_seq_profile, SCALE_WEIGHTS[scale_type])])
        for scale_type in range(3)
    ]
    return argmax(scale_scores)


def abs_note_seq_to_music_key(note_seq: List[MusicNote]) -> MusicKey:
    profile = [0] * 12
    for n in note_seq:
        note_duration = n.end - n.start
        pitch_class = n.pitch
        if pitch_class < 0:
            pitch_class += (pitch_class // 12) * 12
        pitch_class = pitch_class % 12
        profile[pitch_class] += note_duration
    key_score = [0] * 12
    for scale_type in range(3):
        w = SCALE_WEIGHTS[scale_type]
        for tonic in range(12):
            _w = w[-tonic:] + w[:-tonic]
            key_score.append(
                sum([a * b for a, b in zip(profile, _w)])
            )
    best_key_index = argmax(key_score)
    best_scale_type, best_tonic = best_key_index//12, best_key_index%12
    best_key = MusicKey(best_scale_type, best_tonic)
    return best_key


def abs_note_seq_to_chrod_seq(
        abs_note_seq: List[MusicNote],
        metre: Metre,
        window_size: str,
        window_step_unit: str) -> List[Chord]:
    """
        the abs_note_seq is expect to be sorted
        the returned chords are ABSOLUTIVE
    """

    assert len(metre) == 2, 'metre is not 2-tuple'
    assert window_size in ('bar', 'beat'), 'window_size should be \'bar\' or \'beat\''
    assert window_step_unit in ('bar', 'beat'), 'window_step should be \'bar\' or \'beat\''

    detected_scale_type, detected_tonic = abs_note_seq_to_music_key(abs_note_seq)

    scale_weight = SCALE_WEIGHTS[detected_scale_type]
    chord_scale_scores = []
    for chord_type in range(4):
        w = CHORD_WEIGHTS[chord_type]
        for root in range(12):
            _w = w[-root:] + w[:-root]
            chord_scale_scores.append(
                sum([a * b for a, b in zip(scale_weight, _w)])
            )

    # get top k possible normalized_chord
    # k = quartile_three(chord_scale_scores)
    k = mean(chord_scale_scores)
    chord_scale_scores = [
        i - k if i > k else NEG_MAX
        for i in chord_scale_scores
    ]
    chord_scale_prob = softmax(chord_scale_scores, temperature=SCALE_TEMPERATURE)

    # print('---')
    # print('\n'.join([
    #     f'{chord_to_str((cid//12), (cid%12)): {csp}'
    #     for cid, csp, in zip(range(48), chord_scale_prob)
    # ]))

    # find chord
    window_start = 0
    window_end = 4 // metre[1] if window_size == 'beat' else metre[0] * 4 // metre[1]
    window_step = 4 // metre[1] if window_step_unit == 'beat' else metre[0] * 4 // metre[1]

    note_seq_end = max(n.end for n in abs_note_seq)

    chord_seq: List[Chord] = []

    while window_start < note_seq_end:
        overlapped_notes = [
            n
            for n in abs_note_seq
            if n.start < window_end and n.end > window_start
        ]
        if len(overlapped_notes) > 0:
            profile = [0] * 12
            for n in overlapped_notes:
                note_overlap_duration = min(n.end, window_end) - max(n.start, window_start)
                pitch_class = n.pitch
                if pitch_class < 0:
                    pitch_class += (pitch_class // 12) * 12
                pitch_class = pitch_class % 12
                profile[pitch_class] += note_overlap_duration

            # if too few notes or no note in this winodw, then ignore
            if sum(profile) < window_step * 0.2:
                window_start += window_step
                window_end += window_step
                continue

            chord_window_score = []
            for chord_type in range(4):
                w = CHORD_WEIGHTS[chord_type]
                for root in range(12):
                    _w = w[-root:] + w[:-root]
                    chord_window_score.append(
                        sum([a * b for a, b in zip(profile, _w)])
                    )
            chord_window_prob = softmax(chord_window_score)
            # print('---\n', window_start, '\n', chord_window_prob)
            chord_window_scale_prob = [
                (csp ** ALPHA) * (cwp ** BETA)
                for cwp, csp in zip(chord_window_prob, chord_scale_prob)
            ]
            best_chord_index = argmax(chord_window_scale_prob)
            best_chord_type, best_root = best_chord_index//12, best_chord_index%12
            best_chord = Chord(best_chord_type, best_root)

            # should we remove repitition?
            # if len(chord_seq) > 0:
            #     if chord_seq[-1] != best_chord:
            #         chord_seq.append(best_chord)
            # else:
            chord_seq.append(best_chord)

        window_start += window_step
        window_end += window_step

    return chord_seq

def normalized_note_seq_to_chrod_seq(
        normalized_note_seq: List[MusicNote],
        tonic: int,
        metre: Metre,
        window_size: str,
        window_step_unit: str) -> List[Chord]:
    """
        the normalized_note_seq is expect to be sorted
        the returned chords are ABSOLUTIVE
    """

    assert len(metre) == 2, 'metre is not 2-tuple'
    assert 0 <= tonic < 12
    assert window_size in ('bar', 'beat'), 'window_size should be \'bar\' or \'beat\''
    assert window_step_unit in ('bar', 'beat'), 'window_step should be \'bar\' or \'beat\''

    abs_note_seq = denormalize_note_seq(normalized_note_seq, tonic)
    chord_list = abs_note_seq_to_chrod_seq(
        abs_note_seq,
        metre,
        window_size,
        window_step_unit
    )
    return chord_list
