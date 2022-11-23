from argparse import ArgumentParser, Namespace
import json
import pickle

from database import MusicDatabase
from detector import abs_note_seq_to_chrod_seq
from musical_things import MusicNote, chord_seq_to_str

def read_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        'dataset_path',
        type=str
    )
    parser.add_argument(
        'query_file_path',
        type=str
    )
    parser.add_argument(
        '--query_format',
        type=str,
        choices=['midi', 'json'],
        default='json',
        help='\'midi\' - A midi file. \
              \'json\' - Object containing an integer 2-tuple as metre, \
              and a list of objects with three keys: "start", "end", and "pitch"'
    )
    return parser.parse_args()


def main():
    args = read_args()
    md: MusicDatabase = pickle.load(open(args.dataset_path, 'rb'))
    if args.query_format == 'json':
        query_song = json.load(open(args.query_file_path, 'r', encoding='utf8'))
        q_metre = query_song['metre']
        q_melody = [MusicNote(start=n['start'], end=n['end'], pitch=n['pitch']) for n in query_song['melody']]
        print('Query metre:', q_metre)
        print('Query melody:', q_melody)

        # ground_truth
        q_key = query_song['key']
        print('Ground truth key:', q_key)
        print('Ground truth record:', md.folksongs[q_key])
        print('Ground truth chrod_seq:', chord_seq_to_str(md.folksong_chrod_seq[q_key]))
        print('Folksong_scale_type:', md.folksong_music_key[q_key])
    else:
        raise NotImplementedError()

    retrieved_keys = md.search_by_abs_note_seq(q_melody, q_metre)

    print(f'Found {len(retrieved_keys)} records')
    for key in retrieved_keys:
        print(md.folksongs[key])
        print('---')

if __name__ == '__main__':
    main()
