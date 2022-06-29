# inverted index

For each config in [inverted_index_configs.json](inverted_index_configs.json), create an inverted index of the form:
```
{
    token: [
        # instance details
        (collection path::str, document index in collection::int, sentence index in doc::int),
        ...
    ],
    ...
}
```

from a set of tokenised collection, each collection (.json) of the form:

```
    [
        # document 
        [
            label,
            list of tokenised sentences as lists
        ],
        ...
    ]

    Returning:
```

## Run
```
python3 inverted_index.py
```
