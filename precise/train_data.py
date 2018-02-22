# Python 3
# Copyright (c) 2017 Mycroft AI Inc.

import json
from argparse import ArgumentParser
from hashlib import md5
from os.path import join, isfile
from typing import *

import numpy as np

from precise.util import find_wavs
from precise.vectorization import load_vector, vectorize_inhibit, vectorize


class TrainData:
    """Class to handle loading of wave data from categorized folders and SQLite dbs"""

    def __init__(self, train_files: Tuple[List[str], List[str]],
                 test_files: Tuple[List[str], List[str]]):
        self.train_files, self.test_files = train_files, test_files

    @classmethod
    def from_folder(cls, folder: str) -> 'TrainData':
        """
        Load a set of data from a structured folder in the following format:
        {prefix}/
            keyword/
                *.wav
            not-keyword/
                *.wav
            test/
                keyword/
                    *.wav
                not-keyword/
                    *.wav
        """
        return cls(find_wavs(folder), find_wavs(join(folder, 'test')))

    @classmethod
    def from_db(cls, db_file: str, db_folder: str) -> 'TrainData':
        """
        Load a set of data from an SQLite database in the following format:
            Column: "final_tag"
            Value: "wake-word" or "not-wake-word"

            Column: "data_id"
            Value: identifier of file such that the following
                   file exists: {db_folder}/{data_id}.wav
        """
        if not db_file:
            return cls(([], []), ([], []))
        if not isfile(db_file):
            raise RuntimeError('Database file does not exist: ' + db_file)
        import dataset

        train_groups = {}
        train_group_file = db_file.replace('db', '') + 'groups.json'
        if isfile(train_group_file):
            with open(train_group_file) as f:
                train_groups = json.load(f)

        db = dataset.connect('sqlite:///' + db_file)
        files = [
            [join(db_folder, i['data_id'] + '.wav') for i in db['data'].find(final_tag=tag)]
            for tag in ['wake-word', 'not-wake-word']
        ]

        train_files, test_files = ([], []), ([], [])
        for label, rows in enumerate(files):
            for fn in rows:
                if not isfile(fn):
                    continue
                if fn not in train_groups:
                    train_groups[fn] = (
                        'test' if md5(fn.encode('utf8')).hexdigest() > 'c' * 32
                        else 'train'
                    )
                {
                    'train': train_files,
                    'test': test_files
                }[train_groups[fn]][label].append(fn)

        with open(train_group_file, 'w') as f:
            json.dump(train_groups, f)

        return cls(train_files, test_files)

    @classmethod
    def from_both(cls, db_file: str, db_folder: str, data_dir: str) -> 'TrainData':
        """Load data from both a database and a structured folder"""
        return cls.from_db(db_file, db_folder) + cls.from_folder(data_dir)

    def load(self, train=True, test=True) -> tuple:
        """
        Load the vectorized representations of the stored data files
        Args:
            train: Whether to load train data
            test: Whether to load test data
        """
        return self.__load(self.__load_files, train, test)

    def load_inhibit(self, train=True, test=True) -> tuple:
        """Generate data with inhibitory inputs created from keyword samples"""

        def loader(kws: list, nkws: list):
            from precise.params import pr
            inputs = np.empty((0, pr.n_features, pr.feature_size))
            outputs = np.zeros((len(kws), 1))
            for f in kws:
                if not isfile(f):
                    continue
                new_vec = load_vector(f, vectorize_inhibit)
                inputs = np.concatenate([inputs, new_vec])

            return self.merge((inputs, outputs), self.__load_files(kws, nkws))

        return self.__load(loader, train, test)

    @staticmethod
    def merge(data_a: tuple, data_b: tuple) -> tuple:
        return np.concatenate((data_a[0], data_b[0])), np.concatenate((data_a[1], data_b[1]))

    @staticmethod
    def parse_args(parser: ArgumentParser) -> Any:
        """Return parsed args from parser, adding options for train data inputs"""
        parser.add_argument('db_folder', help='Folder to load database references from')
        parser.add_argument('-db', '--db-file', default='', help='Database file to use')
        parser.add_argument('-d', '--data-dir', default='{db_folder}',
                            help='Load files from a different directory')
        args = parser.parse_args()
        args.data_dir = args.data_dir.format(db_folder=args.db_folder)
        return args

    def __repr__(self) -> str:
        string = '<TrainData wake_words={kws} not_wake_words={nkws}' \
                 ' test_wake_words={test_kws} test_not_wake_words={test_nkws}>'
        return string.format(
            kws=len(self.train_files[0]), nkws=len(self.train_files[1]),
            test_kws=len(self.test_files[0]), test_nkws=len(self.test_files[1])
        )

    def __add__(self, other: 'TrainData') -> 'TrainData':
        if not isinstance(other, TrainData):
            raise TypeError('Can only add TrainData to TrainData')
        return TrainData((self.train_files[0] + other.train_files[0],
                          self.train_files[1] + other.train_files[1]),
                         (self.test_files[0] + other.test_files[0],
                          self.test_files[1] + other.test_files[1]))

    def __load(self, loader: Callable, train: bool, test: bool) -> tuple:
        return tuple([
            loader(*files) if files else None
            for files in (train and self.train_files,
                          test and self.test_files)
        ])

    @staticmethod
    def __load_files(kw_files: list, nkw_files: list, vectorizer: Callable = vectorize) -> tuple:
        inputs = []
        outputs = []

        def add(filenames, output):
            inputs.extend(load_vector(f, vectorizer) for f in filenames)
            outputs.extend(np.array([output]) for _ in filenames)

        print('Loading keyword...')
        add(kw_files, 1.0)

        print('Loading not-keyword...')
        add(nkw_files, 0.0)

        from precise.params import pr
        return (
            np.array(inputs) if inputs else np.empty((0, pr.n_features, pr.feature_size)),
            np.array(outputs) if outputs else np.empty((0, 1))
        )
