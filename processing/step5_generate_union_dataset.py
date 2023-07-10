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

        # because I find dataframes weird to use, we'll now switch to list structures
        currently_regarded_labels_converted = [(index, row.to_dict()) for index, row in pd.DataFrame.iterrows(currently_regarded_labels)]

        base_range = range(0, len(currently_regarded_labels_converted))
        for i in base_range:
            base_entry = currently_regarded_labels_converted[i]
            base_index = base_entry[0]
            base_label = base_entry[1]

            candidate_range = range(i + 1, len(currently_regarded_labels_converted))
            for j in candidate_range:
                candidate_entry = currently_regarded_labels_converted[j]
                candidate_index = candidate_entry[0]
                candidate_label = candidate_entry[1]

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
    # end loop document_ids

print(f"- {len(annotations_df[annotations_df['delete_me'] == True])} annotations were merged")

print("- Finished generating union dataset")
