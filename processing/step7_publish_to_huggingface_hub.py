# note that step 6 is missing as of now. That would be converting the CSVs/JSONLs
# from steps 5a and 5b to huggingface datasets

import os
from datasets import load_dataset

from project_paths import DATA_DIR

INPUT_DIRS = [
    os.path.join(DATA_DIR, '5a-generate-union-dataset'),
    os.path.join(DATA_DIR, '5b-merge-documents')
]

print("Processing Step 6: Publish dataset to the Hugging Face Hub")
print("- Only the results of processing steps 5a (union dataset) and 5b (merge into one file) are published",
      "  These directories are included:",
    *["  * '" + directory + "'" for directory in INPUT_DIRS],
    sep='\n')

print("- The following files are going to be published:")
publish_files = {
    DATA_DIR: ['README.md'],
    INPUT_DIRS[0]: ['text.csv', 'union_dataset.csv', 'union_dataset.jsonl'],
    INPUT_DIRS[1]: ['merged_into_long_text.csv', 'merged_into_long_text.jsonl']
}
publish_files_list = []
for directory in publish_files:
    print(f"  > {directory}")
    for file in publish_files[directory]:
        publish_files_list.append(os.path.join(directory, file))
        print(f"    * {publish_files_list[-1]}")

print("- Will now upload the dataset to the Hugging Face Hub")
dataset = load_dataset("stevhliu/demo")






