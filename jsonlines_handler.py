"""
Read from and write to doccano's JSON Lines (JSONL) files and/or convert them
to/from pandas DataFrames.
"""
import json
from typing import Union


def read_jsonlines_file(
        filepath: str
) -> list[dict[str, Union[int, str, list[int, int, str]]]]:
    deserialised: list[dict[str, Union[int, str, list[list[int, int, str]]]]]
    deserialised = []

    with (open(filepath) as file):
        line: str
        for line in file:
            o: dict[str, Union[int, str, list[list[int, int, str]]]]
            o = json.loads(line)
            deserialised.append(o)
            # end for
        # end with

    return deserialised
    # end def


def read_several_jsonlines_files(
        filepaths: list[str]
) -> dict[str, list[dict[str, Union[int, str, list[list[int, int, str]]]]]]:
    deserialised: dict[str, list[dict[str, Union[int, str, list[list[int, int, str]]]]]]
    deserialised = {}

    path: str
    for path in filepaths:
        o: list[dict[str, Union[int, str, list[int, int, str]]]]
        o = read_jsonlines_file(path)
        deserialised[path] = o
        # end for

    return deserialised
    # end def


def write_jsonlines_file(
        json_lines: list[dict[str, Union[int, str, list[list[int, int, str]]]]],
        filepath: str
) -> None:
    with open(filepath, "w") as file:
        entry: dict[str, Union[int, str, list[list[int, int, str]]]]
        for entry in json_lines:
            serialised_entry: str = json.dumps(entry)
            file.write(serialised_entry + "\n")
            # end for
        # end with
    # end def
