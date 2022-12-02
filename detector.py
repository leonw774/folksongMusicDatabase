from math import exp
from typing import List

from musical_things import MusicNote, Chord, MusicKey, Metre

# Chord weights
SINGLE_NOTE_W = [25, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4]
MAJOR_THIRD_W = [13, -4, -4, -4, 12, -4, -4, -4, -4, -4, -4, -4]
MINOR_THIRD_W = [13, -4, -4, 12, -4, -4, -4, -4, -4, -4, -4, -4]
MAJOR_TRIAD_W = [9, -4, -4, -4, 8, -4, -4, 9, -4, -4, -4, -4]
MINOR_TRIAD_W = [9, -4, -4, 8, -4, -4, -4, 9, -4, -4, -4, -4]
MAJOR_SEVEN_W = [7, -4, -4, -4, 6, -4, -4, 6, -4, -4, -4, 6]
MINOR_SEVEN_W = [7, -4, -4, 6, -4, -4, -4, 6, -4, -4, 6, -4]
DOMIN_SEVEN_W = [7, -4, -4, -4, 6, -4, -4, 6, -4, -4, 6, -4]

CHORD_WEIGHTS = [
    SINGLE_NOTE_W,
    MAJOR_THIRD_W,
    MINOR_THIRD_W,
    MAJOR_TRIAD_W,
    MINOR_TRIAD_W,
    MAJOR_SEVEN_W,
    MINOR_SEVEN_W,
    DOMIN_SEVEN_W
]

# map the major, minor, domin as the same so that new and old chord detection have same 4 types
CHORD_TYPE_MAP = [0, 1, 1, 3, 3, 7, 7, 7]

# Scale weight
SCALE_MAJOR_W           = [10, -10, 10, -10, 10, 10, -8, 10, -10, 10, -10, 10]
SCALE_NATURAL_MINOR_W   = [10, -10, 10, 10, -10, 10, -8, 10, 10, -10, 10, -10]
SCALE_HARMONIC_MINOR_W  = [10, -10, 10, 10, -10, 10, -10, 10, 10, -10, -10, 10]
SCALE_MELODIC_MINOR_W   = [10, -10, 10, 10, -10, 10, -10, 10, 2, 2, 2, 2]

SCALE_WEIGHTS = [
    SCALE_MAJOR_W,
    SCALE_NATURAL_MINOR_W,
    SCALE_HARMONIC_MINOR_W,
    SCALE_MELODIC_MINOR_W,
]


OLD_CHORD_NOTES = [
    [[0], [], [2], [], [4], [5], [], [7], [], [9], [], []],
    [[0, 4], [], [2, 5], [], [4, 7], [5, 9], [], [7, 11], [], [9, 0], [], []],
    [[0, 4, 7], [], [2, 5, 8], [], [4, 7, 11], [5, 9, 0], [], [7, 11, 2], [], [9, 0, 4], [], []],
    [[0, 4, 7, 11], [], [2, 5, 8, 0], [], [4, 7, 11, 2], [5, 9, 0, 4], [], [7, 11, 2, 5], [], [9, 0, 4, 7], [], []],
]


NEG_MAX = float('-inf')


def argmax(x):
    return max(range(len(x)), key=lambda i: x[i])

def softmax(x, temperature=1.0):
    x = [i / temperature for i in x]
    e_x = list(map(exp, x))
    sum_e_x = sum(e_x)
    return [i / sum_e_x for i in e_x]

def quartile_three(x):
    t = sorted(x)
    k = 3 * len(t) // 4
    if len(t) % 4 <  2:
        return (t[k] + t[k+1])/2
    else:
        return t[k]

def mean(x):
    return sum(x) / len(x)


def denormalize_note_seq(note_seq: List[MusicNote], tonic: int):
    assert 0 <= tonic < 12
    normalized_note_seq = [
        MusicNote(n.start, n.end, n.pitch+tonic)
        for n in note_seq
    ]
    return normalized_note_seq


def abs_note_seq_to_music_key(note_seq: List[MusicNote]) -> MusicKey:
    profile = [0] * 12
    for n in note_seq:
        note_duration = n.end - n.start
        pitch_class = n.pitch
        if pitch_class < 0:
            pitch_class += (pitch_class // 12) * 12
        pitch_class = pitch_class % 12
        profile[pitch_class] += note_duration
    key_score = []
    for scale_type in range(3):
        w = SCALE_WEIGHTS[scale_type]
        for tonic in range(12):
            _w = w[-tonic:] + w[:-tonic]
            key_score.append(
                sum([a * b for a, b in zip(profile, _w)])
            )
    # print(key_score)
    best_key_index = argmax(key_score)
    best_scale_type, best_tonic = best_key_index//12, best_key_index%12
    best_key = MusicKey(best_scale_type, best_tonic)
    return best_key


def abs_note_seq_to_chrod_seq(
        abs_note_seq: List[MusicNote],
        metre: Metre,
        alpha: float = 0.3,
        beta: float = 1.0,
        tau: float = 12) -> List[Chord]:
    """
        the abs_note_seq is expect to be sorted
        the returned chords are ABSOLUTIVE

        alpha and beta control how much chord_scale_prob and chord_window_prob contribute to the final score

            window_score = (chord_scale_prob ** ALPHA) * (chord_window_prob ** BETA)

        tau is the temperature of to use at softmaxing chord_scale_prob.
        we choose to use higher temperature to prevent one chord get all the probability
    """
    assert len(abs_note_seq) > 0, 'Empty abs_note_seq'
    assert len(metre) == 2, 'metre is not 2-tuple'

    detected_scale_type, detected_tonic = abs_note_seq_to_music_key(abs_note_seq)
    # print('detected_scale_type', detected_scale_type)
    # print('detected_tonic', detected_tonic)

    scale_weight = SCALE_WEIGHTS[detected_scale_type]
    chord_scale_scores = []
    for w in CHORD_WEIGHTS:
        for root in range(12):
            _w = w[-root:] + w[:-root]
            chord_scale_scores.append(
                sum([a * b for a, b in zip(scale_weight, _w)])
            )

    # get top half possible normalized_chord: that is 12 in 48
    k = mean(chord_scale_scores)
    chord_scale_scores = [
        i - k if i > k else NEG_MAX
        for i in chord_scale_scores
    ]
    chord_scale_prob = softmax(chord_scale_scores, temperature=tau)

    # print('---')
    # print('\n'.join([
    #     f'{chord_to_str((cid//12), (cid%12)): {csp}'
    #     for cid, csp, in zip(range(48), chord_scale_prob)
    # ]))

    # find chord for each bar
    window_start = 0
    window_end = metre[0] * 4 // metre[1]
    window_step = window_end

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
            for w in CHORD_WEIGHTS:
                for root in range(12):
                    _w = w[-root:] + w[:-root]
                    chord_window_score.append(
                        sum([a * b for a, b in zip(profile, _w)])
                    )
            chord_window_prob = softmax(chord_window_score)
            # print('---\n', window_start, '\n', chord_window_prob)
            chord_window_scale_prob = [
                (csp ** alpha) * (cwp ** beta)
                for csp, cwp in zip(chord_scale_prob, chord_window_prob)
            ]
            best_chord_index = argmax(chord_window_scale_prob)
            best_chord_type, best_root = best_chord_index//12, best_chord_index%12
            best_chord_type = CHORD_TYPE_MAP[best_chord_type]
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


def normalized_note_seq_to_music_key(normalized_note_seq: List[MusicNote], tonic: int) -> MusicKey:
    assert 0 <= tonic < 12
    abs_note_seq = denormalize_note_seq(normalized_note_seq, tonic)
    return abs_note_seq_to_music_key(abs_note_seq)


def normalized_note_seq_to_chrod_seq(
        normalized_note_seq: List[MusicNote],
        tonic: int,
        metre: Metre,
        alpha: float = 0.3,
        beta: float = 1.0,
        tau: float = 12) -> List[Chord]:
    """
        the normalized_note_seq is expect to be sorted
        the returned chords are ABSOLUTIVE
    """

    assert len(metre) == 2, 'metre is not 2-tuple'
    assert 0 <= tonic < 12

    abs_note_seq = denormalize_note_seq(normalized_note_seq, tonic)
    chord_list = abs_note_seq_to_chrod_seq(abs_note_seq, metre, alpha, beta, tau)
    return chord_list


def old_abs_note_seq_to_chrod_seq(abs_note_seq: List[MusicNote], metre: Metre):

    detected_scale_type, detected_tonic = abs_note_seq_to_music_key(abs_note_seq)
    if detected_scale_type > 0:
        detected_tonic += 3
        if detected_tonic > 12:
            detected_tonic -= 12

    tonal_norm_note_seq = [
        MusicNote(n.start, n.end, n.pitch-detected_tonic)
        for n in abs_note_seq
    ]

    window_step = metre[0] * 4 // metre[1]
    window_start = -window_step
    window_end = 0

    note_seq_end = max(n.end for n in abs_note_seq)

    chord_seq: List[Chord] = []

    while window_start < note_seq_end:
        window_start += window_step
        window_end += window_step

        overlapped_notes = [
            n
            for n in tonal_norm_note_seq
            if n.start < window_end and n.end > window_start
        ]
        candidate_list = [(a, b) for a in range(4) for b in range(12)]

        if len(overlapped_notes) > 0:
            profile = [0] * 12
            for n in overlapped_notes:
                note_overlap_duration = min(n.end, window_end) - max(n.start, window_start)
                pitch_class = n.pitch
                if pitch_class < 0:
                    pitch_class += (pitch_class // 12) * 12
                pitch_class = pitch_class % 12
                profile[pitch_class] += note_overlap_duration

            # step 1
            for _ in range(12):
                temp_profile = profile.copy()
                max_freq_note = argmax(profile)
                new_candidate_list = []
                for c in candidate_list:
                    if max_freq_note in OLD_CHORD_NOTES[c[0]][c[1]]:
                        new_candidate_list.append(c)
                if len(new_candidate_list) > 0:
                    candidate_list = new_candidate_list
                temp_profile[max_freq_note] = 0

            if len(candidate_list) == 1:
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
                continue

            # step 2
            # Preserve the minimal-length chords in the candidate_list
            min_chord_type = min(c[0] for c in candidate_list)
            candidate_list = [c for c in candidate_list if c[0] == min_chord_type]

            if len(candidate_list) == 1:
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
                continue

            # step 3
            # Preserve the chords in the candidate_list, whose roots have the maximal occurrence frequency
            candidate_roots = set([c[1] for c in candidate_list])
            temp_profile = [
                p if i in candidate_roots else 0
                for i, p in enumerate(profile)
            ]
            max_freq_root = argmax(temp_profile)
            candidate_list = [c for c in candidate_list if c[1] == max_freq_root]

            if len(candidate_list) == 1:
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
                continue

            # step 4
            # Preserve the chords in the candidate_list, whose fifths have the maximal occurrence frequency
            candidate_fifths = set([(c[1]+7)%12 for c in candidate_list])
            temp_profile = [
                p if i in candidate_fifths else 0
                for i, p in enumerate(profile)
            ]
            max_freq_fifth = argmax(temp_profile)
            candidate_list = [c for c in candidate_list if (c[1]+7)%12 == max_freq_fifth]

            if len(candidate_list) == 1:
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
                continue

            # step 5
            # Preserve the chords in the candidate_list, whose thirds have the maximal occurrence frequency
            candidate_thirds = set([
                OLD_CHORD_NOTES[c[0]][c[1]][1]
                for c in candidate_list
                if len(OLD_CHORD_NOTES[c[0]][c[1]]) > 1
            ])
            temp_profile = [
                p if i in candidate_thirds else 0
                for i, p in enumerate(profile)
            ]
            max_freq_third = argmax(temp_profile)
            candidate_list = [c for c in candidate_list if (c[1]+7)%12 == max_freq_third]

            if len(candidate_list) == 1:
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
            else:
                # step 6
                # Choose the first entry in the candidate_list as the final result
                chord_seq.append(Chord(candidate_list[0][0], candidate_list[0][1]))
    # end while
    return chord_seq

def old_normalized_note_seq_to_chrod_seq(normalized_note_seq: List[MusicNote], tonic: int, metre: Metre):
    assert 0 <= tonic < 12
    abs_note_seq = denormalize_note_seq(normalized_note_seq, tonic)
    return old_abs_note_seq_to_chrod_seq(abs_note_seq, metre)
