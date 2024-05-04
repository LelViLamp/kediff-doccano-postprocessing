import os

import pandas as pd
from pandas import DataFrame

from project_paths import DATA_DIR

INPUT_DIR: str = os.path.join(DATA_DIR, '4a-manually-handle-odd-cases')
OUTPUT_DIR: str = os.path.join(DATA_DIR, '4b-handle-long-annotations')

print("Processing Step 4b: Handle user's input on long annotations")
print(f"- Data imported from '{INPUT_DIR}'")
print(f"- Result will be written to '{OUTPUT_DIR}'")

annotations_path: str = os.path.join(INPUT_DIR, 'automatically_cleaned_annotations.csv')
decisions_path: str = os.path.join(INPUT_DIR, 'long_annotations.csv')
text_path: str = os.path.join(INPUT_DIR, 'text.csv')

annotations_df: DataFrame = pd.read_csv(annotations_path, index_col=0)
decisions_df: DataFrame = pd.read_csv(decisions_path, index_col=0)
text_df: DataFrame = pd.read_csv(text_path, index_col=0)

print(f"- Read {len(decisions_df)} decisions")

remove_us: DataFrame = decisions_df[decisions_df['keep'] == False]
annotations_df.drop(remove_us.index, inplace=True)
print(f"- {len(remove_us)} long annotations were removed")

print(f"- Materialise data")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")

annotations_path_output = os.path.join(OUTPUT_DIR, 'cleaned_annotations.csv')
annotations_df.to_csv(annotations_path_output)
print(f"  * Saved annotations to '{annotations_path_output}'")
text_path_output = os.path.join(OUTPUT_DIR, 'text.csv')
text_df.to_csv(text_path_output)
print(f"  * Saved text to '{annotations_path_output}'")

print("- Finished applying user's decisions on long annotations")
