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
  Annotations for named entity recognition on Oberdeutsche Allgemeine Litteraturzeitung of the first quarter of 1788
---

# OALZ/1788/Q1/NER Annotations

Annotations for named entity recognition (NER) on text extracted from _Oberdeutsche Allgemeine Litteraturueitung_ (OALZ) of the first quarter (January, Febuary, March) of 1788. The scans from which text was extracted can be found at [Bayerische Staatsbibliothek](https://www.digitale-sammlungen.de/de/view/bsb10628753?page=,1).

The following categories were included in the annotation process.

|Tag    |label         |  Count| Total Length| Median Length| Mean Length|    SD|
|:------|:-------------|------:|------------:|-------------:|-----------:|-----:|
|`EVENT`|Event         |    294|        6,090|            18|       20.71| 13.24|
|`LOC`  |Location      |  2,449|       24,417|             9|        9.97|  6.21|
|`MISC` |Miscellaneous |  2,585|       50,654|            14|       19.60| 19.63|
|`ORG`  |Organisation  |  2,479|       34,693|            11|       13.99|  9.33|
|`PER`  |Person        |  7,055|       64,710|             7|        9.17|  9.35|
|`TIME` |Dates & Time  |  1,076|       13,154|             8|       12.22| 10.98|

Each text passage was annotated in [doccano](https://github.com/doccano/doccano) by two or three annotators and their annotations were merged. For details on how this was done, see [LelViLamp/kediff-doccano-postprocessing](https://github.com/LelViLamp/kediff-doccano-postprocessing). In total, the entire text consists of about 1.7m characters. The resulting annotation datasets were published on the [Hugging Face Hub](https://huggingface.co/datasets/LelViLamp/OALZ-1788-Q1-NER-Annotations).

This data set was created in the project _Kooperative Erschließung diffusen Wissens_ ([KEDiff](https://uni-salzburg.elsevierpure.com/de/projects/kooperative-erschließung-diffusen-wissens-ein-literaturwissenscha)), funded by the State of Salzburg.
