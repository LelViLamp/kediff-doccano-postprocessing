---
task_categories:
- token-classification
language:
- de
- la
- fr
- en
tags:
- historical
pretty_name: >-
  Annotations and models for named entity recognition on Oberdeutsche Allgemeine Litteraturzeitung of the first quarter of 1788
---
# OALZ/1788/Q1/NER

A named entity recognition system (NER) was trained on text extracted from _Oberdeutsche Allgemeine Litteraturzeitung_ (OALZ) of the first quarter (January, Febuary, March) of 1788. The scans from which text was extracted can be found at [Bayerische Staatsbibliothek](https://www.digitale-sammlungen.de/de/view/bsb10628753?page=,1). The extraction strategy of the _KEDiff_ project can be found at [`cborgelt/KEDiff`](https://github.com/cborgelt/KEDiff).



## Annotations

Each text passage was annotated in [doccano](https://github.com/doccano/doccano) by two or three annotators and their annotations were cleaned and merged into one dataset. For details on how this was done, see [`LelViLamp/kediff-doccano-postprocessing`](https://github.com/LelViLamp/kediff-doccano-postprocessing). In total, the text consists of about 1.7m characters. The resulting annotation datasets were published on the Hugging Face Hub. There are two versions:

- [`union-dataset`](https://huggingface.co/datasets/LelViLamp/oalz-1788-q1-ner-annotations-union-dataset) contains the texts split into chunks. This is how they were presented in the annotation application doccano. This dataset is the result of preprocessing step 5a.
- [`merged-union-dataset`](https://huggingface.co/datasets/LelViLamp/oalz-1788-q1-ner-annotations-merged-union-dataset) does not retain this split. The text was merged into one long text and annotation, indices were adapted in preprocessing step 5b.

The following categories were included in the annotation process:

| Tag     | Label         | Count | Total Length | Median Annotation Length | Mean Annotation Length |    SD |
|:--------|:--------------|------:|-------------:|-------------------------:|-----------------------:|------:|
| `EVENT` | Event         |   294 |        6,090 |                       18 |                  20.71 | 13.24 |
| `LOC`   | Location      | 2,449 |       24,417 |                        9 |                   9.97 |  6.21 |
| `MISC`  | Miscellaneous | 2,585 |       50,654 |                       14 |                  19.60 | 19.63 |
| `ORG`   | Organisation  | 2,479 |       34,693 |                       11 |                  13.99 |  9.33 |
| `PER`   | Person        | 7,055 |       64,710 |                        7 |                   9.17 |  9.35 |
| `TIME`  | Dates & Time  | 1,076 |       13,154 |                        8 |                  12.22 | 10.98 |

### Data format

Note that there is three versions of the dataset:
- a Huggingface/Arrow dataset,
- a CSV, and
- a JSONL file.

The former two should be used together with the provided `text.csv` to catch the context of the annotation. The latter JSONL file contains the full text.

The **JSONL file** contains lines of this format:

```json
{
  "id": "example-42",
  "text": "Dieses Projekt wurde an der Universität Salzburg durchgeführt",
  "label": [[28, 49, "ORG"], [40, 49, "LOC"]]
}
```

And here are some example entries as used in the CSV and Huggingface dataset:

| `annotation_id` | `line_id`  | `start` | `end` | `label` | `label_text`         | `merged` |
|:----------------|:-----------|--------:|------:|:--------|:---------------------|:--------:|
| $n$             | example-42 |      28 |    49 | ORG     | Universität Salzburg |   ???    |
| $n+1$           | example-42 |      40 |    49 | LOC     | Salzburg             |   ???    |

The columns mean:
- `annotation_id` was assigned internally by enumerating all annotations in the original dataset, which is not published. This value is not present in the JSONL file.
- `line_id` is the fragment of the subdivided text, as shown in doccano. Called `id` in the JSONL dataset.
- `start` index of the first character that is annotated. Included, starts with 0.
- `end` index of the last character that is annotated. Excluded, maximum value is `len(respectiveText)`.
- `label` indicates what the passage indicated by $[start, end)$ was annotated as.
- `label_text` contains the text that is annotated by $[start, end)$. This is not present in the JSONL dataset as it can be inferred from the `text` entry there.
- `merged` indicates whether this annotation is the result of overlapping annotations of the same label. In that case, `annotation_id` contains the IDs of the individual annotations it was constructed of, separated by underscores. This value is not present in the JSONL dataset, and this column is redundant, as it can be inferred from `annotation_id`.



## NER models

Based on the annotations above, six separate NER classifiers were trained, one for each label type. This was done in order to allow overlapping annotations. For example, in the passage "Dieses Projekt wurde an der Universität Salzburg durchgeführt", you would want to categorise "Universität Salzburg" as an organisation while also extracting "Salzburg" as a location.

To achieve this overlap, each text passage must be run through all the classifiers individually and each classifier's results need to be combined. For details on how the training was done and examples of inference time, see [`LelViLamp/kediff-ner-training`](https://github.com/LelViLamp/kediff-ner-training).

The [`dbmdz/bert-base-historic-multilingual-cased`](https://huggingface.co/dbmdz/bert-base-historic-multilingual-cased) tokeniser was used to create historical embeddings. Therefore, it is necessary to use that in order to use these NER models.

The models' performance measures are shown in the following table. Click the model name to find the model on the Huggingface Hub.

| Model                                                              | Selected Epoch | Checkpoint | Validation Loss | Precision |  Recall | F<sub>1</sub> | Accuracy |
|:-------------------------------------------------------------------|:--------------:|-----------:|----------------:|----------:|--------:|--------------:|---------:|
| [`EVENT`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-event) |       1        |     `1393` |         .021957 |   .665233 | .343066 |       .351528 |  .995700 |
| [`LOC`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-loc)     |       1        |     `1393` |         .033602 |   .829535 | .803648 |       .814146 |  .990999 |
| [`MISC`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-misc)   |       2        |     `2786` |         .123994 |   .739221 | .503677 |       .571298 |   968697 |
| [`ORG`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-org)     |       1        |     `1393` |         .062769 |   .744259 | .709738 |       .726212 |  .980288 |
| [`PER`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-per)     |       2        |     `2786` |         .059186 |   .914037 | .849048 |       .879070 |  .983253 |
| [`TIME`](https://huggingface.co/LelViLamp/oalz-1788-q1-ner-time)   |       1        |     `1393` |         .016120 |   .866866 | .724958 |       .783099 |  .994631 |



## Acknowledgements
The data set and models were created in the project _Kooperative Erschließung diffusen Wissens_ ([KEDiff](https://uni-salzburg.elsevierpure.com/de/projects/kooperative-erschließung-diffusen-wissens-ein-literaturwissenscha)), funded by the [State of Salzburg](https://salzburg.gv.at), Austria, and carried out at [Paris Lodron Universität Salzburg](https://plus.ac.at). 🇦🇹
