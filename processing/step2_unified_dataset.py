import os
import pandas as pd

import jsonlines_handler
from project_paths import DATA_DIR
from utils import extract_annotator_name

INPUT_DIR = os.path.join(DATA_DIR, '1-unzip')
OUTPUT_DIR = os.path.join(DATA_DIR, '2-unified-dataset')

files = [os.path.join(INPUT_DIR, file)
         for file in os.listdir(INPUT_DIR)
         if file.endswith('.jsonl') and 'admin' not in file]

print("Processing Step 2: Merge all annotators into one unified dataset")
print(f"- Unzipped data is located at '{INPUT_DIR}'")
print(f"- Dataset will be written to '{OUTPUT_DIR}'")

jsonlines = jsonlines_handler.read_several_jsonlines_files(files)
print(f"- Read JSONlines from {len(jsonlines)} annotator(s)")

print("- increase legibility by renaming path with annotator names")
annotator_names = []
for annotator_path in jsonlines:
    annotator_name = extract_annotator_name(annotator_path)
    annotator_names.append(annotator_name)
for old_name, new_name in zip(list(jsonlines.keys()), annotator_names):
    jsonlines[new_name] = jsonlines.pop(old_name)
del annotator_name, annotator_names, annotator_path, new_name, old_name

# extract text (into one variable) and annotations (into another one) for all annotator
print(f"- extract text and annotations for all {len(jsonlines)} annotators")
all_texts = dict()
all_annotations = dict()

for annotator in jsonlines:
    print(f"  * processing {annotator}'s annotations")
    documents = jsonlines[annotator]
    annotations = dict()

    for document in documents:
        document_id = document['id']
        text = document['text']
        labels = document['label']

        # process raw text and make sure it's the same as for the texts "already seen before"
        if document_id in all_texts:
            if all_texts[document_id] != text:
                print(f"    ID '{document_id}' already exists but text not the same:",
                      f"      - previous text:    '{all_texts[document_id]}'",
                      f"      - this text:        '{text}'", sep='\n')
        else:
            all_texts[document_id] = text

        # accumulate annotations
        annotations[document_id] = labels

    # append annotations
    all_annotations[annotator] = annotations
del annotator, annotations, document, documents, document_id, text, labels

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

