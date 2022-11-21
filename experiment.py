from argparse import ArgumentParser, Namespace
import pickle
from typing import List
import random

from tqdm import tqdm

from database import MusicDatabase
from detector import denormalize_note_seq
from musical_things import MusicNote
from jianpu import (
    jianpu_to_note_seq, JIANPU_PREFIXES, JIANPU_NOTES, JIANPU_SUFFIXES
)

JIANPU_EDITABLES = JIANPU_PREFIXES.union(JIANPU_NOTES).union(JIANPU_SUFFIXES).difference(['^', 'x'])

def read_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        'dataset_path',
        type=str
    )
    parser.add_argument(
        '-n',
        dest='test_number',
        type=int,
        default=1000
    )
    parser.add_argument(
        '--corrupt-number', '-c',
        type=int,
        default=1
    )
    parser.add_argument(
        '--no-deletion',
        action='store_true'
    )
    parser.add_argument(
        '--no-edition',
        action='store_true'
    )
    return parser.parse_args()

def corrupt_jianpu_str(
        jianpu_str: str,
        corrupt_number: int,
        deletion: bool = True,
        edition: bool = True) -> str:

    assert deletion or edition, 'deletion and edition can\'t be all False'

    corrupt_method = ''
    corrupted_jianpu_str = jianpu_str # string is immutable so it is a copy

    for _ in range(corrupt_number):
        if deletion and edition:
            corrupt_method = 'd' if random.randint(0, 1) == 0 else 'e'
        elif deletion:
            corrupt_method = 'd'
        elif edition:
            corrupt_method = 'e'

        if corrupt_method == 'd':
            rand_index = random.randint(0, len(corrupted_jianpu_str)-1)
            corrupted_jianpu_str = corrupted_jianpu_str[:rand_index] + corrupted_jianpu_str[rand_index+1:]
        else:
            rand_index = random.randint(0, len(corrupted_jianpu_str)-1)
            c = corrupted_jianpu_str[rand_index]

            assert c in JIANPU_EDITABLES
            rand_char = random.choice(list(JIANPU_EDITABLES))
            corrupted_jianpu_str = corrupted_jianpu_str[:rand_index] + rand_char + corrupted_jianpu_str[rand_index+1:]
    return corrupted_jianpu_str

def corrupt_note_seq(
        note_seq: List[MusicNote],
        corrupt_number: int,
        deletion: bool = True,
        edition: bool = True) -> List[MusicNote]:

    assert deletion or edition, 'deletion and edition can\'t be all False'

    corrupt_method = ''
    corrupted_note_seq = note_seq.copy()

    for _ in range(corrupt_number):
        if deletion and edition:
            corrupt_method = 'd' if random.randint(0, 1) == 0 else 'e'
        elif deletion:
            corrupt_method = 'd'
        elif edition:
            corrupt_method = 'e'

        if corrupt_method == 'd':
            rand_index = random.randint(0, len(corrupted_note_seq)-1)
            corrupted_note_seq.pop(rand_index)
        else:
            rand_index = random.randint(0, len(corrupted_note_seq)-1)
            pitch_list = [n.pitch for n in corrupted_note_seq]
            max_pitch = max(pitch_list)
            min_pitch = min(pitch_list)
            sigma = (max_pitch - min_pitch) / 2
            rand_index_pitch = pitch_list[rand_index]
            new_pitch = round(random.gauss(rand_index_pitch, sigma))
            corrupted_note_seq[rand_index].pitch = new_pitch

    return corrupted_note_seq


def main():
    args = read_args()
    md: MusicDatabase = pickle.load(open(args.dataset_path, 'rb'))
    rand_folksongs = random.choices(list(md.folksongs.values()), k=args.test_number)

    note_seq_hits= []
    jianpu_hits = []

    for f in tqdm(rand_folksongs):
        note_seq = f.melody
        # print('original  chord_seq:', chord_seq_to_str(md.folksong_chrod_seq[f.key]))
        corrupted_note_seq = corrupt_note_seq(
            note_seq,
            args.corrupt_number,
            edition=(not args.no_edition),
            deletion=(not args.no_deletion)
        )
        abs_corrupted_note_seq = denormalize_note_seq(corrupted_note_seq, f.tonic)
        # print(
        #     'corrupted chord_seq:',
        #     chord_seq_to_str(
        #         abs_note_seq_to_chrod_seq(abs_corrupted_note_seq, f.metre, md.cd_window_size, md.cd_window_step_unit)
        #     )
        # )
        retrieved_folksongs = md.search_by_abs_note_seq(abs_corrupted_note_seq, f.metre)
        # print('# of retrieved_folksongs:', len(retrieved_folksongs))
        note_seq_hits.append((1 if f.key in retrieved_folksongs else 0))

        jianpu_str = f.melody_str
        # print(jianpu_str)
        try_count = 0
        while try_count < 100:
            try:
                corrupted_jianpu_str = corrupt_jianpu_str(
                    jianpu_str,
                    args.corrupt_number,
                    edition=(not args.no_edition),
                    deletion=(not args.no_deletion)
                )
                # print(corrupted_jianpu_str)
                corrupted_jp_str_note_seq = jianpu_to_note_seq(corrupted_jianpu_str, f.time_unit, f.metre)
                abs_corrupted_jp_str_note_seq = denormalize_note_seq(corrupted_jp_str_note_seq, f.tonic)
                retrieved_folksongs = md.search_by_abs_note_seq(abs_corrupted_jp_str_note_seq, f.metre)
                jianpu_hits.append((1 if f.key in retrieved_folksongs else 0))
                break
            except (ValueError, AssertionError):
                try_count += 1

    print('note_seq hit rate:', sum(note_seq_hits) / len(note_seq_hits))
    print('jianpu hit rate:', sum(jianpu_hits) / len(jianpu_hits))


if __name__ == '__main__':
    main()
