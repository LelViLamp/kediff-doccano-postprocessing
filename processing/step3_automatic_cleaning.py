import os

import numpy as np
import pandas as pd

from project_paths import DATA_DIR

INPUT_DIR = os.path.join(DATA_DIR, '2-all-annotations-in-one-file')
OUTPUT_DIR = os.path.join(DATA_DIR, '3-automatic-cleaning')

print("Processing Step 3: Apply heuristics to automatically clean annotations")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

text_path = os.path.join(INPUT_DIR, 'text.csv')
annotations_path = os.path.join(INPUT_DIR, 'annotations.csv')

text_df = pd.read_csv(text_path)
annotations_df = pd.read_csv(annotations_path)
print(f"- Imported {len(text_df)} lines of text and {len(annotations_df)} annotations")

# remove non-NER labels 'ATTENTION', 'POSTCORR', and 'Personal Bookmark'
print("- Remove non-NER labels 'ATTENTION', 'POSTCORR', and 'Personal Bookmark'")
remove_us = annotations_df[
    (annotations_df['label'] == 'ATTENTION') |
    (annotations_df['label'] == 'POSTCORR') |
    (annotations_df['label'] == 'Personal Bookmark')]
annotations_df.drop(remove_us.index, inplace=True)
print(f"  {len(remove_us)} entries were removed, there are now {len(annotations_df)} annotations left")
del remove_us

# merge '?' label into 'MISC'
print(f"- Merge the '?' label into 'MISC'")
rename_us = annotations_df[annotations_df['label'] == '?']
annotations_df['label'].mask(annotations_df['label'] == '?', 'MISC', inplace=True)
print(f"  {len(rename_us)} entries labelled '?' were identified and renamed")
del rename_us

# truncate annotations
# - trailing spaces
# - abbreviations
# - articles (definite and indefinite
print(f"- Clean annotations")
