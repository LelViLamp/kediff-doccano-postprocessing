import os

import pandas as pd
from tqdm import tqdm

from project_paths import DATA_DIR

INPUT_DIR = os.path.join(DATA_DIR, '4b-handle-long-annotations')
OUTPUT_DIR = os.path.join(DATA_DIR, '5-generate-union-dataset')

print("Processing Step 5: Generate union dataset")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

annotations_path = os.path.join(INPUT_DIR, 'cleaned_annotations.csv')
text_path = os.path.join(INPUT_DIR, 'text.csv')

annotations_df = pd.read_csv(annotations_path, index_col=0)

# todo remove this line
annotations_df = annotations_df[annotations_df['line_id'] <= 200]

text_df = pd.read_csv(text_path, index_col=0)

print(f"- Remove annotator column as it is no longer useful")
annotations_df.drop(labels=['annotator'], axis="columns", inplace=True)

print(f"- Add column 'merged' to indicate if label was merged from another label")
annotations_df['merged'] = len(annotations_df) * [False]

print(f"- Add column 'delete_me'")
annotations_df['delete_me'] = len(annotations_df) * [False]

print(f"- Loop over all {len(annotations_df):,} annotations for {len(text_df):,} documents and merge overlapping annotations of the same label")

document_ids = annotations_df['line_id'].sort_values().unique().tolist()
for document_id in tqdm(document_ids):
    # get annotations for current document
    current_annotations = (annotations_df
                           .query(f"line_id == {document_id}")
                           .sort_values(by=['label', 'start', 'end']))

    # only regard labels of the same category for merging
    found_labels = current_annotations['label'].sort_values().unique().tolist()
    for label in found_labels:
        currently_regarded_labels = current_annotations.query(f"label == '{label}'")

        base_range = range(len(currently_regarded_labels))
        for i in base_range:
            base_label = currently_regarded_labels.iloc[i]

            candidate_range = range(i + 1, len(currently_regarded_labels))
            for j in candidate_range:
                if base_label['delete_me']:
                    continue

                candidate_label = currently_regarded_labels.iloc[j]

                if base_label['start'] <= candidate_label['start'] < base_label['end']:
                    # merge into candidate label and delete base_label
                    candidate_label['start'] = min(base_label['start'], candidate_label['start'])
                    candidate_label['end'] = max(base_label['end'], candidate_label['end'])
                    candidate_label['merged'] = True

                    # delete base_label from all regarded datasets
                    base_label['delete_me'] = True

                    # propagate updates of base_label and candidate_label
                    annotations_df.loc[base_label.name] = base_label
                    current_annotations.loc[base_label.name] = base_label
                    currently_regarded_labels.loc[base_label.name] = base_label

                    annotations_df.loc[candidate_label.name] = candidate_label
                    current_annotations.loc[candidate_label.name] = candidate_label
                    currently_regarded_labels.loc[candidate_label.name] = candidate_label
                    # end if merge condition satisfied
                # end loop candidate_range
            # end loop base_range
        # end loop found_labels
    # end loop document_ids

print(f"- {len(annotations_df[annotations_df['delete_me'] == True])} annotations were merged")

print("- Finished generating union dataset")
