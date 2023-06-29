import os
from typing import Tuple

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
# - remove leading articles (definite and indefinite)
# - remove final full stop
print("- Apply heuristics to annotations")
print("  * define functions")


def truncate_spaces(label_text: str,
                    start: int,
                    end: int) -> Tuple[str, int, int]:
    """
    Truncate leading and following spaces of an annotation
    and adapt indices of annotation in case of removed spaces.
    Internally applies str.lstrip() and str.rstrip().

    Parameters
    ----------
    label_text
        string of text that was annotated
    start
        start index (>= 0) of annotation
    end
        end index of annotation (<= len(tag_text))

    Returns
    -------
    Text, start and end index resulting from stripping the annotation.
    """

    # process
    if label_text != label_text.strip():
        # strip from left-hand side
        stripped_text: str = label_text.lstrip()
        if stripped_text != label_text:
            length_difference: int = len(label_text) - len(stripped_text)
            start += length_difference
            label_text = stripped_text

        # strip from right-hand side
        stripped_text = label_text.rstrip()
        if stripped_text != label_text:
            length_difference: int = len(label_text) - len(stripped_text)
            end -= length_difference
            label_text = stripped_text

    return label_text, start, end


def remove_articles(label_text: str,
                    start: int,
                    end: int) -> Tuple[str, int, int]:
    """
    Leading articles should not be included in annotation
    (der, die, das, den, dem, des, d., ein, eine, einen, einem, einer, eines)

    Parameters
    ----------
    label_text
        string of text that was annotated
    start
        start index (>= 0) of annotation
    end
        end index of annotation (<= len(tag_text))

    Returns
    -------
    Text, start and end index resulting from removing the article.
    """

    # determine how many characters need to be removed
    rem_chars: int
    # bestimmter Artikel
    if label_text.lower().startswith(('der ', 'die ', 'das ', 'den ', 'dem ', 'des ', 'd. ')):
        if label_text.lower().startswith('d. '):
            rem_chars = 3
        else:
            rem_chars = 4
    # unbestimmter Artikel
    elif label_text.lower().startswith(("ein ", "eine ", "einen ", "einem ", "einer ", "eines ")):
        rem_chars: int
        if label_text.lower().startswith("ein "):
            rem_chars = 4
        elif label_text.lower().startswith("eine "):
            rem_chars = 5
        else:
            rem_chars = 6
    # no article to be removed
    else:
        rem_chars = 0

    # perform removal
    label_text = label_text[rem_chars:]
    start += rem_chars

    # return
    return label_text, start, end


def remove_final_full_stop_of_abbreviation(label_text: str,
                                           start: int,
                                           end: int) -> Tuple[str, int, int]:
    """
    If last character is a full stop and annotation text's length is maximum 5,
    consider it as an abbreviation and remove the full stop.

    Parameters
    ----------
    label_text
        string of text that was annotated
    start
        start index (>= 0) of annotation
    end
        end index of annotation (<= len(tag_text))

    Returns
    -------
    Annotation text, start index and end index after removal of full stop.
    """

    # perform removal
    if label_text.endswith('.'):
        if len(label_text) <= 5:
            end -= 1
            label_text = label_text[:-1]

    return label_text, start, end


print("  * loop over dataframe and apply heuristics")
for index, row in annotations_df.iterrows():
    label_text = row['label_text']
    start = row['start']
    end = row['end']

    if not isinstance(label_text, str):
        continue

    label_text, start, end = truncate_spaces(label_text, start, end)
    label_text, start, end = remove_articles(label_text, start, end)
    label_text, start, end = remove_final_full_stop_of_abbreviation(label_text, start, end)

    annotations_df.at[index, 'label_text'] = label_text
    annotations_df.at[index, 'start'] = start
    annotations_df.at[index, 'end'] = end
del index, row, label_text, start, end

print("  * applied cleaning heuristics")

automatically_cleaned_path = os.path.join(OUTPUT_DIR, 'automatically_cleaned.csv')
print(f"- Materialise dataframe to '{automatically_cleaned_path}'")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  created non-existing output directory '{OUTPUT_DIR}'")
annotations_df.to_csv(automatically_cleaned_path, index=False)

print("- Finished automatic cleaning")
