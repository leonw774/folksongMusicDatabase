from argparse import ArgumentParser, Namespace
import glob
import json
import pickle
import random
from traceback import format_exc
from typing import List

from tqdm import tqdm

from database import MusicDatabase, Folksong
from musical_things import MusicNote, chord_seq_to_str


def read_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        'dataset_path',
        type=str
    )
    parser.add_argument(
        'output_file_path',
        type=str,
        help='The file path for outputed pickle file'
    )
    parser.add_argument(
        '--old',
        dest='old_chord_detection',
        action='store_true'
    )
    parser.add_argument(
        '-a',
        type=float,
        default=0.3
    )
    parser.add_argument(
        '-b',
        type=float,
        default=1.0
    )
    parser.add_argument(
        '-t',
        type=float,
        default=8.0
    )
    parser.add_argument(
        '-v',
        dest='verbose',
        action='store_true'
    )
    parser.add_argument(
        '--dump-pattree-json',
        action='store_true'
    )
    return parser.parse_args()

def main():
    args = read_args()
    folksong_list:List[Folksong] = []
    all_sm_file_path = glob.glob(f'{args.dataset_path}/**/*.sm', recursive=True)
    total_record = 0
    for sm_file_path in all_sm_file_path:
        # print(sm_file_path)
        with open(sm_file_path, 'r', encoding='utf8', errors='ignore') as f:
            all_lines = f.readlines()
            all_lines += ['\n'] # to find last record
            record_begin_line_index = 0
            record_end_line_index = 0
            for i, l in enumerate(all_lines):
                if l == '\n':
                    record_end_line_index = i
                    record_lines = all_lines[record_begin_line_index : record_end_line_index]
                    if len(record_lines) > 0:
                        total_record += 1
                        try:
                            folksong_list.append(Folksong.from_lines(record_lines))
                        except NotImplementedError:
                            pass
                        except BaseException:
                            print(f'Exception @ line {i} in {sm_file_path}.')
                            print(format_exc())
                    record_begin_line_index = i + 1
                    record_end_line_index = i + 1
    print(f'successfully parsed {len(folksong_list)} out of {total_record} records')

    md = MusicDatabase(
        folksong_list,
        old_chord_detection=args.old_chord_detection,
        alpha=args.a,
        beta=args.b,
        tau=args.t
    )
    print('PAT-tree number of nodes:', len(md.pat_tree))
    if args.verbose:
        for k, f in md.folksongs.items():
            print('-'*8)
            print(f)
            print('Music key:', md.folksong_music_key[k])
            print('Chord sequence:', chord_seq_to_str(md.folksong_chrod_seq[k], is_old=args.old_chord_detection))
    pickle.dump(md, open(args.output_file_path, 'wb+'), protocol=pickle.HIGHEST_PROTOCOL)

    # dump json of PAT-tree
    if args.dump_pattree_json:
        with open('pat_tree.json', 'w+', encoding='utf8') as f:
            f.write(json.dumps(md.pat_tree.head.to_dict(), default=lambda o: o.__dict__, sort_keys=True, indent=2))

    # output a random query json file
    # rand_folksong = random.choice(list(md.folksongs.values()))
    # q_rand_fs = {
    #     'metre': rand_folksong.metre,
    #     'key': rand_folksong.key,
    #     # de-normalize the melody so no tonic was needed
    #     'melody': [MusicNote(n.start, n.end, n.pitch+rand_folksong.tonic) for n in rand_folksong.melody]
    # }
    # with open('test_query.json', 'w+', encoding='utf8') as f:
    #     f.write(json.dumps(q_rand_fs, default=lambda o: o.__dict__, sort_keys=True))

if __name__ == '__main__':
    main()
