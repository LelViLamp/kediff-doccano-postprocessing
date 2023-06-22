import os

import pandas as pd

import jsonlines_handler
from project_paths import DATA_DIR

INPUT_DIR = os.path.join(DATA_DIR, '1-unzip')
OUTPUT_DIR = os.path.join(DATA_DIR, '2-put-into-one-dataset')

files = [os.path.join(INPUT_DIR, file)
         for file in os.listdir(INPUT_DIR)
         if file.endswith('.jsonl') and 'admin' not in file]

jsonlines = jsonlines_handler.read_several_jsonlines_files(files)

# we need a text variable (list) for each line to store the text
all_texts = dict()
all_annotations = dict()

for annotator in jsonlines:
    documents = jsonlines[annotator]
    annotations = dict()

    for document in documents:
        document_id, text, labels = document['id'], document['text'], document['label']

        # process raw text
        if document_id in all_texts:
            if all_texts[document_id] != text:
                print(f"- ID '{document_id}' already exists but text not the same:",
                      f"    * previous text:    '{all_texts[document_id]}'",
                      f"    * this text:        '{text}'",
                      sep='\n')
        else:
            all_texts[document_id] = text

        # accumulate annotations
        annotations[document_id] = labels

    # append annotations
    all_annotations[annotator] = annotations

# data frame for all annotations
all_entries = list()
for annotator in all_annotations:
    annotator_entries = list()
    annotations = all_annotations[annotator]

    for line_id in annotations:
        labels = annotations[line_id]
        for annotation in labels:
            start = annotation[0]
            end = annotation[1]
            label = annotation[2]

            line_text = all_texts[line_id]
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

    all_entries.extend(annotator_entries)

df = pd.DataFrame(all_entries)

# df as csv

