import os
from typing import List, Dict, Union

import pandas as pd
from pandas import DataFrame

import jsonlines_handler
from project_paths import DATA_DIR
from utils import extract_annotator_name

INPUT_DIR: str = os.path.join(DATA_DIR, '1-unzip')
OUTPUT_DIR: str = os.path.join(DATA_DIR, '2-all-annotations-in-one-file')

print("Processing Step 2: Merge all annotators into one unified dataset")
print(f"- Unzipped data is located at '{INPUT_DIR}'")
print(f"- Dataset will be written to '{OUTPUT_DIR}'")

# get JSON Lines file and read all of them, except for admin.jsonl
files: list[str] = [
    os.path.join(INPUT_DIR, file)
    for file in os.listdir(INPUT_DIR)
    if file.endswith('.jsonl') and 'admin' not in file
]
print(f"- Identified {len(files)} relevant files to be read")

jsonlines: dict[str, list[dict[str, Union[int, str, list[list[int, int, str]]]]]]
jsonlines = jsonlines_handler.read_several_jsonlines_files(files)
print(f"- Imported JSON Lines from {len(jsonlines)} annotator(s)")

print("- Increase legibility by renaming keys from input file path to annotator names")
annotator_names: list[str] = []
annotator_path: str
for annotator_path in jsonlines:
    annotator_name: str = extract_annotator_name(annotator_path)
    annotator_names.append(annotator_name)
old_key: str
new_key: str
for old_key, new_key in zip(list(jsonlines.keys()), annotator_names):
    jsonlines[new_key] = jsonlines.pop(old_key)
del annotator_name, annotator_names, annotator_path, new_key, old_key

# extract text (into one variable) and annotations (into another one) for all annotator
print(f"- Extract text and annotations for all {len(jsonlines)} annotators")
texts_dict: dict[int, str] = {}
annotations_dict: dict[str, dict[int, list[int, int, str]]] = {}

annotator: str
for annotator in jsonlines:
    print(f"  * Processing {annotator}'s annotations")
    documents: list[dict[str, Union[int, str, list[int, int, str]]]]
    documents = jsonlines[annotator]
    annotations: dict[int, list[int, int, str]]
    annotations = {}

    document: dict[str, Union[int, str, list[int, int, str]]]
    for document in documents:
        document_id: int = document['id']
        text: str = document['text']
        labels: list[int, int, str] = document['label']

        # process raw text and make sure it's the same as for the texts "already seen before"
        if document_id in texts_dict:
            if texts_dict[document_id] != text:
                print(f"    ID '{document_id}' already exists but text not the same:",
                      f"      - previous text:    '{texts_dict[document_id]}'",
                      f"      - this text:        '{text}'", sep='\n')
        else:
            texts_dict[document_id] = text

        # accumulate annotations
        annotations[document_id] = labels

    # append annotations
    annotations_dict[annotator] = annotations
del annotator, annotations, document, documents, document_id, text, labels

# data frame for all annotations
print("- Generate dataframe for annotations")
df_entries_list: list[dict[str, Union[int, str]]] = []
for annotator in annotations_dict:
    # todo this can be done much more elegantly by avoiding the double for-loop
    annotator_entries: list[dict[str, Union[int, str]]] = []
    annotations = annotations_dict[annotator]

    line_id: int
    for line_id in annotations:
        labels: list[int, int, str] = annotations[line_id]
        for annotation in labels:
            start: int = annotation[0]
            end: int = annotation[1]
            label: str = annotation[2]

            line_text: str = texts_dict[line_id]
            line_text_length: int = len(line_text)
            label_text: str = line_text[start:end]
            label_text_length: int = len(label_text)

            new_entry: dict[str, Union[int, str]] = {
                'annotator': annotator,
                'line_id': line_id,
                'start': start,
                'end': end,
                'label': label,
                'label_text': label_text
            }
            annotator_entries.append(new_entry)

    df_entries_list.extend(annotator_entries)

annotations_df: DataFrame = pd.DataFrame(df_entries_list)

print("- Generate dataframe for texts")
texts_df: DataFrame = pd.DataFrame.from_dict(texts_dict, orient='index')
texts_df.rename(columns={0: 'text'}, inplace=True)

# materialise the results
texts_path: str = os.path.join(OUTPUT_DIR, "text.csv")
annotations_path: str = os.path.join(OUTPUT_DIR, "annotations.csv")

print(f"- Materialise dataframes to '{texts_path}' and '{annotations_path}'")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")
texts_df.to_csv(texts_path, index_label='document_id')
annotations_df.to_csv(annotations_path, index_label='annotation_id')

print("- Finished creating unified dataset")
