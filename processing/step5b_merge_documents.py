import json
import os
import pandas as pd
from tqdm import tqdm

import jsonlines_handler
from project_paths import DATA_DIR

INPUT_DIR = os.path.join(DATA_DIR, '5a-generate-union-dataset')
OUTPUT_DIR = os.path.join(DATA_DIR, '5b-merge-documents')

print("Processing Step 5b: Merge documents into one text")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

annotations_path_in_jsonl = os.path.join(INPUT_DIR, 'union_dataset.jsonl')
text_path = os.path.join(INPUT_DIR, 'text.csv')

annotations_jsonl = jsonlines_handler.read_jsonlines_file(annotations_path_in_jsonl)
text_df = pd.read_csv(text_path, index_col=0)

# merge lines and change label indices
merged_document_id = ""
merged_text = ""
merged_labels = []
merge_count = 0

print(f"- Merge text into one line and merge labels that overlap document boundaries")
for document in tqdm(annotations_jsonl):
    current_document_id = document['id']
    current_text = document['text']
    current_labels = document['label']

    offset = len(merged_text) + 1

    # identify labels that need to be merged
    # already merged ones: those finishing at last character of text
    base_merge_candidates = [label for label in merged_labels if label[1] == len(merged_text)]
    # in currently added document, this is those starting at first character, i.e. at index 0
    current_merge_candidates = [label for label in current_labels if label[0] == 0]

    # loop over all annotations, those that have the same label need to be merged
    for base_candidate in base_merge_candidates:
        for current_candidate in current_merge_candidates:
            if base_candidate[2] == current_candidate[2]:
                # merge current_candidate into base_candidate by reference
                base_candidate[1] += current_candidate[1] + 1
                merge_count += 1

                # no longer consider current_candidate with non-merged current_labels
                if current_candidate in current_labels:
                    current_labels.remove(current_candidate)

    # adapt indices of current_labels
    for current_label in current_labels:
        current_label[0] += offset
        current_label[1] += offset

    # store result in merged_* variables
    merged_document_id = f"{merged_document_id}_{current_document_id}"
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

jsonl = {
    "text": merged_text,
    "label": merged_labels
}
print(f"  * created JSONL object")

annotations_path_out_jsonl = os.path.join(OUTPUT_DIR, 'merged_into_long_text.json')
with open(annotations_path_out_jsonl, "w") as f:
    f.write(json.dumps(jsonl))
print(f"  * Saved merged annotations as JSONL to '{annotations_path_out_jsonl}'")

# find annotation/label's text
for label in merged_labels:
    start = label[0]
    end = label[1]
    label_text = merged_text[start:end]
    label.append(label_text)
    # end loop merged_labels
csv = pd.DataFrame(merged_labels, columns =['start', 'end', 'label', 'label_text'])
print(f"  * created dataframe including label_text")

annotations_path_out_csv = os.path.join(OUTPUT_DIR, 'merged_into_long_text.csv')
csv.to_csv(annotations_path_out_csv)
print(f"  * Saved merged annotations as CSV to '{annotations_path_out_csv}'")

# save raw/merged text
text_path_out = os.path.join(OUTPUT_DIR, "text.csv")
text_df.to_csv(text_path_out)
print(f"  * Saved text to '{text_path_out}'")

print("- Finished merging into one long text")
