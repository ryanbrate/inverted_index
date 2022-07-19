""" Create an inverted index 

    Each tokenized (.json) collection assumed to be of the form:

    [
        [
            document label::str,
            [
                [], # sentence as a list of tokens
                ...
            ]  # list of sentences
        ], # document in the collection 
        ...
    ]  # collection

    Returning inverted index (as .json):

    { 
        token::str{
            collection_path::str:[
                (document index::int, sentence index in doc::int),  # instance
                ...
            ],  # all instances the token appears in the collection
            ...
        },
        ...
    }

"""
import json
import pathlib
import typing
from collections import defaultdict
from functools import reduce
from functools import partial
from multiprocessing import Pool
from itertools import cycle

from tqdm import tqdm


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

        config_name:str = pathlib.Path(config["name"])
        input_dir = pathlib.Path(config["input_dir"]).expanduser()
        output_dir = pathlib.Path(config["output_dir"]).expanduser()
        n_processes:int = int(config["n_processes"])
        tokens_of_interest: list[str] = config["tokens_of_interest"]

        # already sampled ... skip
        if output_dir.exists():

            print(f"{output_dir} exits ... skipping")
            continue  # skip config if looks like it's already been run

        else:

            print(f"getting inverted index for {config_name}")

            # iterable of collections paths in input_dir
            collections_paths: list[pathlib.Path] = [
                p for p in input_dir.glob("*.json") if p.name != "config.json"
            ]

            # get a list of inverted indices for each collection in input_dir
            print(f"\tassembling indices for each collection...")
            if n_processes == 1:

                # single-threaded index assembly
                indices: list[dict] = []
                for collection_path in tqdm(collections_paths):
                    indices.append(get_index(collection_path, tokens_of_interest))

            else:

                # multi-threaded index assembly
                with Pool(n_processes) as p:
                    indices = p.starmap(get_index, zip(collections_paths, cycle([tokens_of_interest])))

            print(f"\tassembling smaller indices into one larger index")

            # create global hash
            big_index = defaultdict(lambda: defaultdict(list))
            for collection_path, index in indices:
                for token, v in index.items():
                    big_index[token][collection_path] += v

            # create the output dir
            output_dir.mkdir(exist_ok=True, parents=True)

            # save the index
            with open(output_dir / "inverted_index.json", "w") as f:
                json.dump(big_index, f, ensure_ascii=False)

            # save a copy of the config
            with open(output_dir / "config.json", "w") as f:
                json.dump(config, f, ensure_ascii=False)



def get_index(collection_path: pathlib.Path, tokens_of_interest: list[str])->tuple:
    """Return an index of tokens_of_interest wrt., the collection at collection_path.

    Args:
        collection_path
        tokens_of_interest

    Return the tuple (collection_path::str, index), where index is:

        {
            token::str: [
                (document index::int, sentence index in doc::int),  # instance
                    ...
            ],  # all instances the token appears in the collection
                ...
        } 
    """

    index = defaultdict(list)

    with open(collection_path, "r") as f:
        collection = json.load(f)

    for i, (label, doc) in enumerate(collection):
        for j, sent in enumerate(doc):
            for token in set(sent):
                if token in tokens_of_interest or len(tokens_of_interest)==0:
                    index[token].append((i, j))

    return (str(collection_path), index)


if __name__ == "__main__":
    main()
