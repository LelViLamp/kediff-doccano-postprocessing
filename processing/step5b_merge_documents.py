import json
import os
from typing import List, Dict, Union, Any

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

import jsonlines_handler
from project_paths import DATA_DIR

INPUT_DIR: str = os.path.join(DATA_DIR, '5a-union-dataset')
OUTPUT_DIR: str = os.path.join(DATA_DIR, '5b-long-text')

print("Processing Step 5b: Merge documents into one text")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

annotations_path_in_jsonl: str = os.path.join(INPUT_DIR, 'union_dataset.jsonl')
text_path: str = os.path.join(INPUT_DIR, 'text.csv')

annotations_jsonl: list[dict[str, Union[int, str, list[int, int, str]]]] = jsonlines_handler.read_jsonlines_file(annotations_path_in_jsonl)
text_df: DataFrame = pd.read_csv(text_path, index_col=0)

# merge lines and change label indices
merged_document_id: str = ""
merged_text: str = ""
merged_labels: list[list[int, int, str]] = []
merge_count: int = 0

print(f"- Merge text into one line and merge labels that overlap document boundaries")
document: dict[str, Union[int, str, list[int, int, str]]]
for document in tqdm(annotations_jsonl):
    current_document_id: str = document['id']
    current_text: str = document['text']
    current_labels: list[int, int, str] = document['label']

    offset: int = len(merged_text) + 1

    # identify labels that need to be merged
    # already merged ones: those finishing at last character of text
    base_merge_candidates: list[list[int, int, str]] = [
        label for label in merged_labels
        if label[1] == len(merged_text)
    ]
    # in currently added document, this is those starting at first character, i.e. at index 0
    current_merge_candidates: list[list[int, int, str]] = [
        label for label in current_labels
        if label[0] == 0
    ]

    # loop over all annotations, those that have the same label need to be merged
    base_candidate: list[int, int, str]
    for base_candidate in base_merge_candidates:
        current_candidate: list[int, int, str]
        for current_candidate in current_merge_candidates:
            if base_candidate[2] == current_candidate[2]:
                # merge current_candidate into base_candidate by reference
                base_candidate[1] += current_candidate[1] + 1
                merge_count += 1

                # no longer consider current_candidate with non-merged current_labels
                if current_candidate in current_labels:
                    current_labels.remove(current_candidate)

    # adapt indices of current_labels
    current_label: list[int, int, str]
    for current_label in current_labels:
        current_label[0] += offset
        current_label[1] += offset

    # store result in merged_* variables
    merged_document_id: str = f"{merged_document_id}_{current_document_id}"
    merged_text += " " + current_text
    merged_labels = [*merged_labels, *current_labels]
    pass

if merged_document_id.startswith('_'):
    merged_document_id = merged_document_id[1:]
    pass

print(f"  * {merge_count} annotations were merged")

print(f"- Materialise merged text and annotations to {OUTPUT_DIR}")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")

jsonl: dict[str, Union[str, list[list[int, int, str]]]] = {
    "text": merged_text,
    "label": merged_labels
}
print(f"  * created JSONL object")

annotations_path_out_jsonl: str = os.path.join(OUTPUT_DIR, 'merged_into_long_text.json')
with open(annotations_path_out_jsonl, "w") as f:
    f.write(json.dumps(jsonl))
print(f"  * Saved merged annotations as JSONL to '{annotations_path_out_jsonl}'")

# find annotation/label's text
label: list[int, int, str]
for label in merged_labels:
    start: int = label[0]
    end: int = label[1]
    label_text: str = merged_text[start:end]

    label.append(label_text)
    # end loop merged_labels
csv: DataFrame = pd.DataFrame(merged_labels, columns =['start', 'end', 'label', 'label_text'])
print(f"  * created dataframe including label_text")

annotations_path_out_csv: str = os.path.join(OUTPUT_DIR, 'merged_into_long_text.csv')
csv.to_csv(annotations_path_out_csv)
print(f"  * Saved merged annotations as CSV to '{annotations_path_out_csv}'")

# save raw/merged text
text_path_out: str = os.path.join(OUTPUT_DIR, "text.csv")
text_df.to_csv(text_path_out)
print(f"  * Saved text to '{text_path_out}'")

print("- Finished merging into one long text")
