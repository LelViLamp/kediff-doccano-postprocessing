"""
Read from and write to doccano's JSON Lines (JSONL) files and/or convert them
to/from pandas DataFrames.
"""
import json
from typing import Any


def read_jsonlines_file(filepath: str):
    deserialised = list()

    with open(filepath) as file:
        for line in file:
            o: Any = json.loads(line)
            deserialised.append(o)

    return deserialised


def read_several_jsonlines_files(filepaths: list[str]):
    deserialised = dict()

    for path in filepaths:
        o = read_jsonlines_file(path)
        deserialised[path] = o

    return deserialised
