"""
A record in Essen Folksong Database has structure :

    ALTDEU  // Name of the subsection
    CUT[Title of the song]
    TRD[Source of the tune: book, tape etc.]
    KEY[Signature TimeUnit Tonic Metre]
    MEL[
        melody in Jianpu
        (A melody is a sequence of tonal normalized notes)
    ]
    FKT|FCT[Function - dance, lullaby, wedding song etc.]
    CMT[Comment]
    TXT[Lyrics]


Our music database created from Essen Folksong Database will have:

- A "folksong" table:
    - Attributes:
        - Name of subsection
        - Song title
        - Signature, TimeUnit, Tonic, Metre
        - Melody in 3-tuple format and its original jianpu string
        - Lyrics
    - The key attrbiutes of this table is {Song title, Signature}
- Two new tables:
    - A "chord_seq" table to store detected scale type of each folksong
        - Attributes: {Song titleg, Signature, Chord sequence}
    - A "scale_type" table to store detected chord sequence of each folksong
        - Attributes: {Song titleg, Signature, Scale type}

Reference:

    - http://www.cs.uu.nl/events/dech1999/dahlig/tsld001.htm
    - https://ldzhangyx.github.io/2019/07/26/esac/

"""

from typing import List, Mapping, Set, Tuple

from tqdm import tqdm

from musical_things import MusicNote, Chord, Metre, NOTE_NAME_TO_NUMBER, NOTE_NAME, chord_to_str, chord_seq_to_str
from detector import (
    normalized_note_seq_to_scale_type,
    abs_note_seq_to_chrod_seq,
    normalized_note_seq_to_chrod_seq
)
from jianpu import jianpu_to_note_seq


FolksongKey = str

TITLE_TAG = 'CUT'
KEY_TAG = 'KEY'
MELODY_TAG = 'MEL'
LYRICS_TAG = 'TXT'

class Folksong:
    def __init__(self,
            subset: str,
            title: str,
            signature: str,
            time_unit: int,
            tonic: int,
            metre: Metre,
            melody: List[MusicNote],
            melody_str: str,
            lyrics: str) -> None:
        self.subset = subset
        self.title = title
        self.signature = signature
        self.time_unit = time_unit
        self.tonic = tonic
        self.metre = metre
        self.melody = melody
        self.melody_str = melody_str
        self.lyrics = lyrics

    def __str__(self):
        return f'{self.subset} - {self.signature}\n'\
            f'Title: {self.title}\n'\
            f'Time unit: {round(4 / self.time_unit)}\n'\
            f'Tonic: {NOTE_NAME[self.tonic]}\n'\
            f'Metre: {self.metre[0]}/{self.metre[1]}\n'\
            f'Melody: {self.melody}\n'\
            f'Lyrics: {self.lyrics}'\

    @property
    def key(self):
        # return (self.title, self.signature, self.time_unit, self.tonic)
        return ':'.join(map(str, (self.title, self.signature)))

    @classmethod
    def from_lines(cls, lines: List[str]) -> 'Folksong':
        deseperated_lines:List[str] = []
        filename = lines[0].rstrip()
        for l in lines[1:]:
            if l.startswith('    '): # 4 spaces
                deseperated_lines[-1] += (' ' + l.strip())
            else:
                deseperated_lines.append(l.rstrip())

        title = ""
        signature = ""
        time_unit = 0
        tonic = -1
        metre = (0, 0)
        melody = ""
        melody_str = ""
        lyrics = ""
        for l in deseperated_lines:
            if l.startswith(TITLE_TAG):
                title = l[4:-1]
            elif l.startswith(KEY_TAG):
                keys_str = l[4:-1]
                perc_exist = keys_str.find('%')
                if perc_exist != -1:
                    keys_str = keys_str[:perc_exist]

                signature = keys_str[:7]
                signature = signature.rstrip()

                unit_note_str = keys_str[7:9]
                time_unit = 1 / (int(unit_note_str) / 4) # quarter note = 1

                tonic_str = keys_str[9:12]
                tonic_str = tonic_str.lstrip()
                tonic = NOTE_NAME_TO_NUMBER[tonic_str]

                metre_str = keys_str[12:]
                metre_str = metre_str.lstrip()
                if metre_str.find(' ') != -1:
                    additive_metres = [
                        tuple(map(int, m.split('/')))
                        for m in metre_str.split()
                    ]
                    if all(m[1] == additive_metres[0][1] for m in additive_metres):
                        mean_numerator = sum(m[0] for m in additive_metres) / len(additive_metres)
                        metre = (mean_numerator, additive_metres[0][1])
                    else:
                        raise NotImplementedError('Additive metres with different dominator not supported.')
                else:
                    if metre_str.startswith('FREI'):
                        raise NotImplementedError('Free metre not supported.')
                    else:
                        metre = tuple(map(int, metre_str.split('/')))

            elif l.startswith(MELODY_TAG):
                begin_index = l.index('[') + 1
                try:
                    end_index = l.index('//]')
                except ValueError:
                    end_index = l.index(']')
                melody_str = l[begin_index:end_index]
                melody_str = melody_str.replace('  ', '|').replace(' ', '') # use "|"as measure line
                melody_str = melody_str.lstrip('|') # remove empty measures at beggining
                try:
                    melody = jianpu_to_note_seq(melody_str, time_unit, metre)
                except Exception as e:
                    print(deseperated_lines)
                    print(f'{title}\n{signature}\n{time_unit}\n{tonic}\n{metre}\n{melody_str}\n{lyrics}')
                    print(repr(e))
                    raise e
            elif l.startswith(LYRICS_TAG):
                lyrics = l[4:-1]
        return cls(filename, title, signature, time_unit, tonic, metre, melody, melody_str, lyrics)

class PATTreeNode:
    def __init__(self, nid) -> None:
        self.nid = nid
        self.children: Mapping[List[Chord], PATTreeNode] = dict()
        self.keys: Set[FolksongKey] = set()

    def get_subtree_keys(self) -> Set[FolksongKey]:
        res_set = set(self.keys)
        # recursive
        for v in self.children.values():
            res_set.update(v.get_subtree_keys())
        return res_set

    def to_dict(self) -> dict:
        return {
            'nid': self.nid,
            'children': {
                ','.join([chord_to_str(c) for c in k]): v.to_dict()
                for k, v in self.children.items()
            },
            'keys': list(self.keys)
        }

    def __repr__(self) -> str:
        return str(vars(self))

    def __len__(self) -> int:
        return 1 + sum(len(n) for n in self.children.values())


class PATTree:
    def __init__(self) -> None:
        self.head = PATTreeNode(0)
        self.node_number = 1

    def __len__(self) -> int:
        return self.node_number

    def insert(self, chord_seq: Tuple[Chord], key: FolksongKey) -> None:
        si_seqs = [
            chord_seq[i:]
            for i in range(len(chord_seq))
        ]
        for sis in si_seqs:
            # print('sis:', chord_seq_to_str(sis))
            sis = tuple(sis)
            cur_node = self.head
            while len(sis) > 0:
                # scan current node's link for any sequence that starts the same as sis
                # print('  at node', cur_node.nid)
                found_same_start = 0
                for link, child_node in cur_node.children.items():
                    for i in range(1, min(len(sis), len(link))+1):
                        sis_start = sis[:i]
                        if all(i == j for i, j in zip(sis_start, link)):
                            found_same_start = i
                        else:
                            break
                    if found_same_start > 0:
                        # print('  link to', child_node.nid, ':', chord_seq_to_str(link), 'found_same_start:', found_same_start)
                        if found_same_start < len(link):
                            # link is longer than sis
                            # have to insert a new node between cur_node and cur_children[link]
                            # Old: cur_node -- link --> child_node
                            # New: cur_node -- link[:found_same_start] --> new_node
                            # new_node.children = {
                            #     link[found_same_start:]: child_node,
                            # }
                            new_node = PATTreeNode(self.node_number)
                            self.node_number += 1
                            cur_node.children[link[:found_same_start]] = new_node
                            new_node.children[link[found_same_start:]] = child_node
                            # print(
                            #     '  link split: add new node', new_node.nid,
                            #     chord_seq_to_str(link[:found_same_start]),
                            #     'and', chord_seq_to_str(link[found_same_start:])
                            # )
                            del cur_node.children[link]
                            child_node = new_node

                        if found_same_start == len(sis):
                            # print('  add key')
                            child_node.keys.add(key)
                            sis = [] # leave while loop
                        else:
                            sis = sis[found_same_start:]
                        # update
                        cur_node = child_node
                        break

                # no link found
                if found_same_start == 0:
                    cur_node.children[sis] = PATTreeNode(self.node_number)
                    self.node_number += 1
                    # print('  create node', cur_node.children[sis].nid, 'and add key')
                    cur_node.children[sis].keys.add(key)
                    cur_node = cur_node.children
                    sis = []
                    break

    def search(self, chord_seq: List[Chord]) -> Set[FolksongKey]:
        s = list(chord_seq)
        cur_node = self.head
        while len(s) > 0:
            # print("s", chord_seq_to_str(s))
            found_same_start = 0
            # print(len(cur_node.children), len(cur_node.keys))
            for link, child_node in cur_node.children.items():
                for i in range(1, min(len(s), len(link))+1):
                    s_start = s[:i]
                    if all(i == j for i, j in zip(s_start, link)):
                        found_same_start = i
                    else:
                        break

                if found_same_start > 0:
                    # print('  link to', child_node.nid, ':', chord_seq_to_str(link), 'found_same_start:', found_same_start)
                    if found_same_start == len(s):
                        # found
                        s = [] # leave while loop
                    else:
                        # keep going
                        s = s[found_same_start:]
                    # update
                    cur_node = child_node
                    break

            if found_same_start == 0:
                # print('no matching links')
                return set()
        # end while
        return cur_node.get_subtree_keys()

    def delete(self, chord_seq: List[Chord], semi_infinite: bool = False):
        raise NotImplementedError()


class MusicDatabase:
    def __init__(self, Folksong_list: List[Folksong], cd_window_size: str, cd_window_step_unit: str) -> None:
        self.folksongs = {
            f.key: f
            for f in Folksong_list
        }
        # check that key is unique
        if len(self.folksongs) != len(Folksong_list):
            sigs = set()
            for f in Folksong_list:
                if f.key not in sigs:
                    sigs.add(f.key)
                else:
                    raise AssertionError(f'{f.key} repeated at {f}')
        self.folksong_scale_type: Mapping[FolksongKey, int] = dict()
        self.folksong_chrod_seq: Mapping[FolksongKey, List[Chord]] = dict()
        self.cd_window_size = cd_window_size
        self.cd_window_step_unit = cd_window_step_unit
        self.pat_tree = PATTree()
        for s, f in tqdm(self.folksongs.items(), desc='Creating PAT-tree...'):
            scale_type = normalized_note_seq_to_scale_type(f.melody)
            self.folksong_scale_type[f.key] = scale_type
            detected_chord_seq = normalized_note_seq_to_chrod_seq(
                f.melody, f.tonic, f.metre, cd_window_size, cd_window_step_unit
            )
            # print(chord_seq_to_str(detected_chord_seq))
            self.folksong_chrod_seq[f.key] = detected_chord_seq
            self.pat_tree.insert(detected_chord_seq, s)

    def search_by_abs_note_seq(self, q_abs_note_seq: List[MusicNote], metre: Metre) -> Set[FolksongKey]:
        chord_seq = abs_note_seq_to_chrod_seq(q_abs_note_seq, metre, self.cd_window_size, self.cd_window_step_unit)
        # print('search_by_abs_note_seq: dected chord:', chord_seq_to_str(chord_seq))
        retrieved_signatures = self.pat_tree.search(chord_seq)
        return retrieved_signatures

    def to_dict(self) -> dict:
        return {
            'folksongs': self.folksongs,
            'folksong_scale_type': self.folksong_scale_type,
            'folksong_chrod_seq': self.folksong_chrod_seq,
            'cd_window_size': self.cd_window_size,
            'cd_window_step_unit': self.cd_window_step_unit,
            'pat_tree': {
                'head': self.pat_tree.head.to_dict()
            }
        }
