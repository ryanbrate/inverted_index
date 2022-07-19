# inverted index

For each config in [inverted_index_configs.json](inverted_index_configs.json), create an inverted index of the form:
```
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
```

from a dir of tokenised collections (i.e., from the tokenize module), each collection (.json) of the form:

```
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
```

## Run
```
python3 inverted_index.py
```

## config notes:

* All instances of config.json in config["input_dir"] are ignored
* where "tokens_of_interest" in config is non-blank, only those words are collected in the index.
