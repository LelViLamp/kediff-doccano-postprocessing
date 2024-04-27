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

A named entity recognition system (NER) was trained on text extracted from _Oberdeutsche Allgemeine Litteraturueitung_ (OALZ) of the first quarter (January, Febuary, March) of 1788. The scans from which text was extracted can be found at [Bayerische Staatsbibliothek](https://www.digitale-sammlungen.de/de/view/bsb10628753?page=,1) using the extraction strategy of the _KEDiff_ project, which can be found at [`cborgelt/KEDiff`](https://github.com/cborgelt/KEDiff).

## Annotations

Each text passage was annotated in [doccano](https://github.com/doccano/doccano) by two or three annotators and their annotations were cleaned and merged into one dataset. For details on how this was done, see [`LelViLamp/kediff-doccano-postprocessing`](https://github.com/LelViLamp/kediff-doccano-postprocessing). In total, the text consists of about 1.7m characters. The resulting annotation datasets were published on the Hugging Face Hub as [`OALZ-1788-Q1-NER-Annotations`](https://huggingface.co/datasets/LelViLamp/OALZ-1788-Q1-NER-Annotations).

The following categories were included in the annotation process:

| Tag     | Label         | Count | Total Length | Median Annotation Length | Mean Annotation Length |    SD |
| :------ | :------------ | ----: | -----------: | -----------------------: | ---------------------: | ----: |
| `EVENT` | Event         |   294 |        6,090 |                       18 |                  20.71 | 13.24 |
| `LOC`   | Location      | 2,449 |       24,417 |                        9 |                   9.97 |  6.21 |
| `MISC`  | Miscellaneous | 2,585 |       50,654 |                       14 |                  19.60 | 19.63 |
| `ORG`   | Organisation  | 2,479 |       34,693 |                       11 |                  13.99 |  9.33 |
| `PER`   | Person        | 7,055 |       64,710 |                        7 |                   9.17 |  9.35 |
| `TIME`  | Dates & Time  | 1,076 |       13,154 |                        8 |                  12.22 | 10.98 |

## NER models

Based on the annotations above, six separate NER classifiers were trained, one for each label type. This was done in order to allow overlapping annotations. For example, you would want to categorise the whole passage "Universität Salzburg" as an organisation while also extracting "Salzburg" as a location. This would result in an annotation like this:

```json
{
  "text": "Universität Salzburg",
  "label": [[0, 20, "ORG"], [12, 20, "LOC"]]
}
```

To achieve this overlap, each text passage must be run through all the classifiers individually and each classifier's results need to be combined. For details on how the training was done, see [`LelViLamp/kediff-ner-training`](https://github.com/LelViLamp/kediff-ner-training).

The models' performance measures are as follows:

| Model                                                              | Selected Epoch | Checkpoint | Validation Loss | Precision |  Recall |   $F_1$ | Accuracy |
| :----------------------------------------------------------------- | :------------: | ---------: | --------------: | --------: | ------: | ------: | -------: |
| [`EVENT`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-EVENT) |       1        |     `1393` |         .021957 |   .665233 | .343066 | .351528 |  .995700 |
| [`LOC`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-LOC)     |       1        |     `1393` |         .033602 |   .829535 | .803648 | .814146 |  .990999 |
| [`MISC`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-MISC)   |       2        |     `2786` |         .123994 |   .739221 | .503677 | .571298 |   968697 |
| [`ORG`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-ORG)     |       1        |     `1393` |         .062769 |   .744259 | .709738 | .726212 |  .980288 |
| [`PER`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-PER)     |       2        |     `2786` |         .059186 |   .914037 | .849048 | .879070 |  .983253 |
| [`TIME`](https://huggingface.co/LelViLamp/OALZ-1788-Q1-NER-TIME)   |       1        |     `1393` |         .016120 |   .866866 | .724958 | .783099 |  .994631 |

## Acknowledgements
The data set and models were created in the project _Kooperative Erschließung diffusen Wissens_ ([KEDiff](https://uni-salzburg.elsevierpure.com/de/projects/kooperative-erschließung-diffusen-wissens-ein-literaturwissenscha)), funded by the [State of Salzburg](https://salzburg.gv.at), Austria 🇦🇹, and carried out at [Paris Lodron Universität Salzburg](https://plus.ac.at).
