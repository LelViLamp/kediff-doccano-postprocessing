import os
import pandas as pd

import jsonlines_handler
from project_paths import DATA_DIR
from utils import extract_annotator_name

INPUT_DIR = os.path.join(DATA_DIR, '1-unzip')
OUTPUT_DIR = os.path.join(DATA_DIR, '2-all-annotations-in-one-file')

print("Processing Step 2: Merge all annotators into one unified dataset")
print(f"- Unzipped data is located at '{INPUT_DIR}'")
print(f"- Dataset will be written to '{OUTPUT_DIR}'")

# get JSONlines fils and read all of them
files = [os.path.join(INPUT_DIR, file)
         for file in os.listdir(INPUT_DIR)
         if file.endswith('.jsonl') and 'admin' not in file]
print(f"- Identified {len(files)} relevant files to be read")

jsonlines = jsonlines_handler.read_several_jsonlines_files(files)
print(f"- Imported JSONlines from {len(jsonlines)} annotator(s)")

print("- Increase legibility by renaming path with annotator names")
annotator_names = []
for annotator_path in jsonlines:
    annotator_name = extract_annotator_name(annotator_path)
    annotator_names.append(annotator_name)
for old_name, new_name in zip(list(jsonlines.keys()), annotator_names):
    jsonlines[new_name] = jsonlines.pop(old_name)
del annotator_name, annotator_names, annotator_path, new_name, old_name

# extract text (into one variable) and annotations (into another one) for all annotator
print(f"- Extract text and annotations for all {len(jsonlines)} annotators")
texts_dict = dict()
annotations_dict = dict()

for annotator in jsonlines:
    print(f"  * Processing {annotator}'s annotations")
    documents = jsonlines[annotator]
    annotations = dict()

    for document in documents:
        document_id = document['id']
        text = document['text']
        labels = document['label']

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
df_entries_list = list()
for annotator in annotations_dict:
    # todo this can be done much more elegantly by avoiding the double for-loop
    annotator_entries = list()
    annotations = annotations_dict[annotator]

    for line_id in annotations:
        labels = annotations[line_id]
        for annotation in labels:
            start = annotation[0]
            end = annotation[1]
            label = annotation[2]

            line_text = texts_dict[line_id]
            line_text_length = len(line_text)
            label_text = line_text[start:end]
            label_text_length = len(label_text)

            new_entry = {
                'annotator': annotator,
                'line_id': line_id,
                'start': start,
                'end': end,
                'label': label,
                'label_text': label_text
            }
            annotator_entries.append(new_entry)

    df_entries_list.extend(annotator_entries)

annotations_df = pd.DataFrame(df_entries_list)

print("- Generate dataframe for texts")
texts_df = pd.DataFrame.from_dict(texts_dict, orient='index')
texts_df.rename(columns={0: 'text'}, inplace=True)

# materialise the results
texts_path = os.path.join(OUTPUT_DIR, "text.csv")
annotations_path = os.path.join(OUTPUT_DIR, "annotations.csv")

print(f"- Materialise dataframes to '{texts_path}' and '{annotations_path}'")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")
texts_df.to_csv(texts_path, index_label='document_id')
annotations_df.to_csv(annotations_path, index_label='annotation_id')

print("- Finished creating unified dataset")
