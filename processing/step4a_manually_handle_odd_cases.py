import os
from typing import List

import pandas as pd
from pandas import DataFrame

from project_paths import DATA_DIR

INPUT_DIR: str = os.path.join(DATA_DIR, '3-automatic-cleaning')
OUTPUT_DIR: str = os.path.join(DATA_DIR, '4a-manually-handle-odd-cases')

print("Processing Step 4a: Manually identify and handle odd cases")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

text_path: str = os.path.join(INPUT_DIR, 'text.csv')
annotations_path: str = os.path.join(INPUT_DIR, 'automatically_cleaned_annotations.csv')

text_df: DataFrame = pd.read_csv(text_path)
annotations_df: DataFrame = pd.read_csv(annotations_path)

# start >= len(label_text) or end >= len(label_text)
nan_texts: DataFrame = annotations_df[annotations_df['label_text'].isnull()]
print(f"- Identified {len(nan_texts)} annotations that have a NULL text")

# join annotations with text
joined = pd.merge(
    left=annotations_df,
    right=text_df,
    left_on='line_id',
    right_on='document_id'
)

# start or end is greater than actual text's length
invalid_ranges: DataFrame = joined[
    (joined['start'] > joined['text'].str.len()) |
    (joined['end'] > joined['text'].str.len())]
print(f"  * {len(invalid_ranges)} are longer than their base text")

annotations_df.drop(invalid_ranges.index, inplace=True)
joined.drop(invalid_ranges.index, inplace=True)
print("    They were removed")

zero_character_annotations: DataFrame = annotations_df[annotations_df['start'] == annotations_df['end']]
print(f"  * {len(zero_character_annotations)} do not contain a character")

annotations_df.drop(zero_character_annotations.index, inplace=True)
joined.drop(zero_character_annotations.index, inplace=True)
print("    They were removed")

# len(label_text) >= 100
long_annotations: DataFrame = annotations_df[annotations_df['label_text'].str.len() >= 100]
decisions: list[bool] = len(long_annotations) * [True]
long_annotations['keep'] = decisions
print(f"- Identified {len(long_annotations)} annotations that are 100 or more characters long")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")

long_annotations_path: str = os.path.join(OUTPUT_DIR, 'long_annotations.csv')
long_annotations.to_csv(long_annotations_path)
print(f"  * Stored them to '{long_annotations_path}'",
      f"  * Please indicate whether you want to keep them by changing 'keep' to 'False'",
      f"    for those rows that you would like to remove",
      sep='\n')

annotations_path_output: str = annotations_path.replace(INPUT_DIR, OUTPUT_DIR)
annotations_df.to_csv(annotations_path_output)
print(f"  * Stored cleaned annotations to '{annotations_path_output}'")
text_path_output = text_path.replace(INPUT_DIR, OUTPUT_DIR)
text_df.to_csv(text_path_output)
print(f"  * Stored text to '{text_path_output}'")

print("- Finished manual cleaning")
