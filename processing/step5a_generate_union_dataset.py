import os
from typing import Any, Tuple, Union, Dict, List

import pandas as pd
from collections import defaultdict

from pandas import DataFrame, Series
from tqdm import tqdm

import jsonlines_handler
from project_paths import DATA_DIR

INPUT_DIR: str = os.path.join(DATA_DIR, '4b-handle-long-annotations')
OUTPUT_DIR: str = os.path.join(DATA_DIR, '5a-union-dataset')

print("Processing Step 5a: Generate union dataset")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

annotations_path_input: str = os.path.join(INPUT_DIR, 'cleaned_annotations.csv')
text_path_input: str = os.path.join(INPUT_DIR, 'text.csv')

annotations_df: DataFrame = pd.read_csv(annotations_path_input, index_col=0)
text_df: DataFrame = pd.read_csv(text_path_input, index_col=0)

# annotations_df = annotations_df[:200] # for debug

print(f"- Remove annotator column as it is no longer useful")
annotations_df.drop(labels=['annotator'], axis="columns", inplace=True)

print(f"- Add column 'merged' to indicate if label was merged from another label")
annotations_df['merged'] = len(annotations_df) * [False]

print(f"- Add column 'delete_me'")
annotations_df['delete_me'] = len(annotations_df) * [False]

print(f"- Loop over all {len(annotations_df):,} annotations for {len(text_df):,} documents and merge overlapping "
        f"annotations of the same label")
document_ids: list[int] = annotations_df['line_id'].sort_values().unique().tolist()
merge_result_defdict: defaultdict[int, defaultdict[str, list[tuple[int, dict[str, Union[bool, int, str]]]]]]
merge_result_defdict = defaultdict(lambda: defaultdict(lambda: list()))
document_id: int
for document_id in tqdm(document_ids):
    # get annotations for current document
    current_annotations: DataFrame = (
        annotations_df
        .query(f"line_id == {document_id}")
        .sort_values(by=['label', 'start', 'end'])
    )

    # only regard labels of the same category for merging
    found_labels: list[str] = current_annotations['label'].sort_values().unique().tolist()

    label: str
    for label in found_labels:
        currently_regarded_labels: DataFrame = current_annotations.query(f"label == '{label}'")

        # because I find dataframes weird to use, we'll now switch to list structures
        currently_regarded_labels_converted: list[tuple[int, dict[str, Union[bool, int, str]]]]
        index: int
        row: Series
        currently_regarded_labels_converted = [
            (index, row.to_dict())
            for index, row in pd.DataFrame.iterrows(currently_regarded_labels)
        ]

        base_range: range = range(0, len(currently_regarded_labels_converted))
        i: int
        for i in base_range:
            base_entry: tuple[int, dict[str, bool | int | str]] = currently_regarded_labels_converted[i]
            base_index: int = base_entry[0]
            base_label: dict[str, Union[bool, int, str]] = base_entry[1]

            candidate_range: range = range(i + 1, len(currently_regarded_labels_converted))
            j: int
            for j in candidate_range:
                candidate_entry: tuple[int, dict[str, Union[bool, int, str]]] = currently_regarded_labels_converted[j]
                candidate_index: int = candidate_entry[0]
                candidate_label: dict[str, Union[bool, int, str]] = candidate_entry[1]

                if base_label['start'] <= candidate_label['start'] < base_label['end']:
                    # merge into candidate label and delete base_label
                    candidate_label['start'] = min(base_label['start'], candidate_label['start'])
                    candidate_label['end'] = max(base_label['end'], candidate_label['end'])

                    base_label['delete_me'] = True
                    candidate_label['merged'] = True
                    candidate_label['annotation_id'] = "_".join([str(base_label['annotation_id']), str(candidate_label['annotation_id'])])

                    # label_text for candidate_label
                    candidate_label['label_text'] = text_df.loc[candidate_label['line_id'] - 1]['text'][candidate_label['start']:candidate_label['end']]

                    # because we merged, we need to (manually) change the looping behaviour to disregard
                    # no-more-existent base_label
                    break
                    # end if merge condition satisfied
                # end loop candidate_range

            # if base_label was merged into candidate_label, make candidate_label
            # new base_label, i.e., move on in for loop
            if base_label['delete_me']:
                continue
            # end loop base_range
        # end loop found_labels

        merge_result_defdict[document_id][label] = currently_regarded_labels_converted
    merge_result_defdict[document_id] = merge_result_defdict[document_id]
    # end loop document_ids

# convert to dictionaries
print(f"- Converting defaultdicts to dicts")
merge_result: dict[int, dict[str, list[tuple[int, dict[str, bool | int | str]]]]]
merge_result = {}
line_id: int
for line_id in tqdm(merge_result_defdict):
    local_merge_result_defdict: defaultdict[str, list[tuple[int, dict[str, bool | int | str]]]]
    local_merge_result_defdict = merge_result_defdict[line_id]
    local_merge_result_dict = dict(local_merge_result_defdict)
    merge_result[line_id] = local_merge_result_dict

print(f"- Merge result generated. Now apply it to dataframe")
deletionCount: int = 0
unchangedCount: int = 0
updateCount: int = 0

for document_id in tqdm(merge_result):
    labels: dict[str, list[tuple[int, dict[str, Union[bool, int, str]]]]] = merge_result[document_id]
    for label in labels:
        annotations: list[tuple[int, dict[str, Union[bool, int, str]]]] = labels[label]
        updated_annotation: dict[str, Union[bool, int, str]]
        for index, updated_annotation in annotations:
            if updated_annotation['delete_me']:
                annotations_df.drop(index, inplace=True)
                deletionCount += 1
            elif updated_annotation['merged']:
                updateCount += 1
                key: str
                for key in updated_annotation:
                    # for easier
                    current = annotations_df.loc[index, key]
                    updated = updated_annotation[key]
                    annotations_df.loc[index, key] = updated_annotation[key]
            else:
                unchangedCount += 1
            # end loop over annotations
        # end loop over labels
    # end loop over documents

print(f"- {updateCount:,} annotations were merged, which caused {deletionCount:,} annotations to be deleted.",
        f"{unchangedCount:,} annotations were left unchanged.",
      sep=" ")

print(f"- Remove 'delete_me' column as it only contains 'False' now")
annotations_df.drop(['delete_me'], axis="columns", inplace=True)

print(f"- Generate JSON Lines object")
json_lines = []
# loop over dataframe
document_ids: list[int] = annotations_df['line_id'].sort_values().unique().tolist()
line: list[int, str, list[list[int, int, str]]]
for _, line in tqdm(text_df.iterrows(), total=len(text_df)):
    entry: dict[str, Union[int, str, list[list[int, int, str]]]]
    entry = {
        "id": line[0],
        "text": line[1],
        "label": []
    }

    if entry['id'] in document_ids:
        doc_annotations = annotations_df.query(f"line_id == {entry['id']}")
        for _, values in pd.DataFrame.iterrows(doc_annotations):
            start: int = values['start']
            end: int = values['end']
            label: str = values['label']

            label_list: list[int, int, str] = [start, end, label]
            entry['label'].append(label_list)
        # end if has annotations

    json_lines.append(entry)
    # end loop over text_df's lines

print(f"- Materialise union dataset to {OUTPUT_DIR}")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")

annotations_path_out_csv: str = os.path.join(OUTPUT_DIR, 'union_dataset.csv')
annotations_df.to_csv(annotations_path_out_csv)
print(f"  * Saved merged annotations as CSV to '{annotations_path_out_csv}'")

annotations_path_out_jsonl: str = os.path.join(OUTPUT_DIR, 'union_dataset.jsonl')
jsonlines_handler.write_jsonlines_file(json_lines, annotations_path_out_jsonl)
print(f"  * Saved merged annotations as JSONL to '{annotations_path_out_jsonl}'")

text_path_out: str = os.path.join(OUTPUT_DIR, "text.csv")
text_df.to_csv(text_path_out)
print(f"  * Saved text to '{text_path_out}'")

print("- Finished generating union dataset")
