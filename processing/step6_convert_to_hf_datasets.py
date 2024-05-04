import os

import datasets
from datasets import Dataset, Value, Features, ClassLabel
import pandas as pd
from pandas import DataFrame

from processing.project_paths import DATA_DIR

INPUT_CSVs = {'5a': os.path.join(DATA_DIR, "5a-union-dataset", "union_dataset.csv"),
              '5b': os.path.join(DATA_DIR, "5b-long-text", "merged_into_long_text.csv"), }

print("Processing Step 6: Convert to HuggingFace datasets")


##############
# Process 5a #
##############

path: str = INPUT_CSVs['5a']
print(f"- now processing data of '{os.path.relpath(path)}'")

filename: str = os.path.basename(path)
filename_no_ext: str = os.path.splitext(filename)[0]
input_directory: str = os.path.dirname(path)
output_directory: str = os.path.join(input_directory, filename_no_ext)

union_df: DataFrame = pd.read_csv(
    filepath_or_buffer=path,
    index_col="annotation_id"
)
union_df = union_df.drop(labels="Unnamed: 0", axis=1)
union_hf: Dataset = Dataset.from_pandas(df=union_df, preserve_index=True)
union_hf = union_hf.cast(features=Features({
    "annotation_id": Value(dtype="string"),
    "line_id": Value(dtype="uint16"),
    "start": Value(dtype="uint16"),
    "end": Value(dtype="uint16"),
    "label": ClassLabel(names=sorted(union_df["label"].unique().tolist())),
    "label_text": Value(dtype="string"),
    "merged": Value(dtype="bool"),
}))
union_hf.info.homepage = "https://github.com/cborgelt/KEDiff"
union_hf.info.description = \
    """
    Merged annotations on text extracted from the first quarter of 1788's "Oberdeutsche Allgemeine
    Litteraturzeitung" (OALZ), provided by Bayerische Staatsbibliothek. Text fragments were left as they
    were. See 5a's 'text.csv' or JSONL file to see the text that the annotations' indices (start, end)
    refer to. 
    """
union_hf.save_to_disk(dataset_path=output_directory)


##############
# Process 5b #
##############

path: str = INPUT_CSVs['5b']
print(f"- now processing data of '{os.path.relpath(path)}'")

filename: str = os.path.basename(path)
filename_no_ext: str = os.path.splitext(filename)[0]
input_directory: str = os.path.dirname(path)
output_directory: str = os.path.join(input_directory, filename_no_ext)

long_df: DataFrame = pd.read_csv(filepath_or_buffer=path, index_col=0)
long_hf: Dataset = Dataset.from_pandas(df=long_df, preserve_index=False, )
long_hf = long_hf.cast(features=Features({
    "start": Value(dtype="uint32"),
    "end": Value(dtype="uint32"),
    "label": ClassLabel(names=sorted(long_df["label"].unique().tolist())),
    "label_text": Value(dtype="string"),
}))
long_hf.info.homepage = "https://github.com/cborgelt/KEDiff"
long_hf.info.description = \
    """
    Merged annotations on text extracted from the first quarter of 1788's "Oberdeutsche Allgemeine
    Litteraturzeitung" (OALZ), provided by Bayerische Staatsbibliothek. Text fragments were merged into
    one long text. See 5b's 'text.csv' or JSONL file to see the text that the annotations' indices (start,
    end) refer to.
    """
long_hf.save_to_disk(dataset_path=output_directory)
