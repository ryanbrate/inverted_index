""" From a tokenised set create an inverted index. 
    Each tokenized collection assumed to be of the form:

    [
        # document 
        [
            label,
            list of tokenised sentences as lists
        ],
        ...
    ]

    Returning:

    {
        token: [
            # instance details
            (collection path::str, document index in collection::int, sentence index in doc::int),
            ...
        ],
        ...
    }

"""
import json
import pathlib
import typing
from collections import defaultdict
from functools import reduce
from itertools import chain
from copy import deepcopy

import spacy


def main():

    # ------
    # load the configs
    # ------

    with open("inverted_index_configs.json", "r") as f:
        configs: list[dict] = json.load(f)

    # ------
    # iterate over each sampling configuration
    # ------
    for config in configs:

        input_dir = pathlib.Path(config["input_dir"]).expanduser()
        output_dir = pathlib.Path(config["output_dir"]).expanduser()

        # already sampled ... skip
        if output_dir.exists():

            print(f"{output_dir} exits ... skipping")
            continue  # skip config if looks like it's already been run

        else:

            # iterable of collections paths
            collections_paths: list[pathlib.Path] = [
                p for p in input_dir.glob("*.json") if p.name != "config.json"
            ]

            # get indexes for each collection path
            indices: list[dict] = [
                get_index(collection_path) for collection_path in collections_paths
            ]

            # accumulate into 
            index = reduce(combine_indices, indices)

            # create the output dir
            output_dir.mkdir(exist_ok=True, parents=True)

            # save
            with open(output_dir / "inverted_index.json", "w") as f:
                json.dump(index, f, indent=4, ensure_ascii=True)


def get_index(collection_path: pathlib.Path):
    """Return an index of token wrt., the collection at collection_path.

    Args:

    Return:
        {
            token: [
                (collection path::str, doc index::int, sent index::int),
                ...
            ],
            ...
        }
    """

    index = defaultdict(list)

    with open(collection_path, "r") as f:
        collection = json.load(f)

    for i, (label, doc) in enumerate(collection):
        for j, sent in enumerate(doc):
            for token in set(sent):
                index[token].append((str(collection_path), i, j))

    return index


def combine_indices(indexA:defaultdict, indexB:defaultdict):
    """Return a single index, from an iterable of indices."""

    index = deepcopy(indexA)

    for token in indexB.keys():
        index[token] += indexB[token]

    return index


if __name__ == "__main__":
    main()
