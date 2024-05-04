import os
from typing import List, Dict, Any

from datasets import load_dataset, Dataset

from project_paths import DATA_DIR

INPUT_DIRS: list[str] = [
    os.path.join(DATA_DIR, '5a-generate-union-dataset'),
    os.path.join(DATA_DIR, '5b-merge-documents'),
    os.path.join(DATA_DIR, '6-huggingface-datasets')
]
REPO_ID_BASE: str = "oalz-1788-q1-ner-annotations-"

print("Processing Step 7: Publish datasets to the Hugging Face Hub")
print(f"- Only the results of processing steps",
      f"  * 5a (union dataset),",
      f"  * 5b (merge into one file), and",
      f"  * 6 (converted to HF datasets)",
      f"  are published",
      f"- These directories are included:",
    *[f"  * '{directory}'" for directory in INPUT_DIRS],
      sep='\n')

print("- This means that the following files/directories are going to be published:")
publish_files: dict[str, list[str]] = {
    "general": ["README.md"],
    "5a-generate-union-dataset": [
        "text.csv",
        "union_dataset.csv",
        "union_dataset.jsonl",
        "union_dataset/"
    ],
    "5b-merge-documents": [
        "merged_into_long_text.csv",
        "merged_into_long_text.jsonl",
        "merged_into_long_text/"
    ]
}

union_repo_id: str = REPO_ID_BASE + "union-dataset"
print(f"- Will now publish 5a as '{union_repo_id}'")
union_dir: str = os.path.join(
    DATA_DIR,
    list(publish_files.keys())[1],
    publish_files["5a-generate-union-dataset"][-1]
)
union_hf: Dataset = Dataset.load_from_disk(dataset_path=union_dir)
union_hf.push_to_hub(repo_id=union_repo_id)

long_repo_id: str = REPO_ID_BASE + "merged-union-dataset"
print(f"- Will now publish 5b as '{long_repo_id}'")
long_dir: str = os.path.join(
    DATA_DIR,
    list(publish_files.keys())[2],
    publish_files["5b-merge-documents"][-1]
)
long_hf: Dataset = Dataset.load_from_disk(dataset_path=union_dir)
long_hf.push_to_hub(repo_id=long_repo_id)

print("- please upload the remaining files, i.e. CSVs, JSONLs, and README.md -> MANUALLY<- ")

pass
