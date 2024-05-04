# Postprocessing and generation of the OALZ/1788/Q1-NER Datasets

Postprocessing pipeline on the doccano annotations to create the OALZ/1788/Q1-NER datasets happened in several steps. After placing the raw files in the correct directory as described in step 0, the pipeline can be run as a whole using `processing/run_all.py`. Each step corresponds to a separate script and temporary output directory. Scripts tell you what they did on the console. This is especially useful for checking and debugging file paths.

| Step | Short description                               | Name Input Directory                |
|:----:|:------------------------------------------------|:------------------------------------|
|  0   | Place doccano ZIP file containing JSONLs        | `0-raw`                             |
|  1   | Extract ZIP file                                | `0-raw`                             |
|  2   | Merge all annotations into one CSV file         | `1-unzip`                           |
|  3   | Automatically clean annotations                 | `2-all-annotations-in-one-file`     |
|  4a  | Manually handle odd cases                       | `3-automatic-cleaning`              |
|      | **_Manual user input expected_**                |                                     |
|  4b  | Apply user's decision                           | `4a-manually-hanlde-odd-cases`      |
|  5a  | Remove references to annotators, merge overlaps | `4b-handle-long-annotations`        |
|  5b  | Merge passages into long text.                  | `5a-union-dataset`                  |
|  6   | Convert to HuggingFace Datasets                 | `5a-union-dataset` & `5b-long-text` |
|  7   | Upload to HuggingFace Hub                       | `5a-union-dataset` & `5b-long-text` |

0. Annotate the dataset, export a ZIP file from [doccano](https://github.com/doccano/doccano) and move it to `data/0-raw`. Use JSONL as the output format. The file name should begin with a timestamp of the format `YYYY-MM-DD_HHMM` to allow ordering the files in descending order and automatically pick the latest export. This allows re-running the processing pipeline without any additional changes.
1. Identifies the latest ZIP file by file name as described above and extracts it. This results in one [JSON Lines file](https://jsonlines.org) per user associated with the project in doccano, including the _admin_, which gets ignored subsequently. A JSONL file contains one valid JSON string per line.
2. Merge all annotators' JSONL files into one CSV file. This uses `jsonlines_handler.py` and `utils.py`
3. Automatically clean annotations by applying heuristics:
   * remove labels `ATTENTION`, `POSTCORR`, and `Personal Bookmark` as they are not used for named entity recognition (NER). These labels could be placed and were used for correcting the text extraction using optical character recognition (OCR) or to allow annotators to highlight text passages they personally found interesting.
   * The `?` label was merged into the `MISC` label as all annotators said they used them interchangeably.
   * Annotations were truncated, i.e., based on they text they refer to, parts of that annotation would be removed by adapting their `start` and `end` indices.
     * Leading and trailing spaces were removed using `str.lstrip` and `str.rstrip`.
     * If an annotation started with a German article, that would be removed as the annotators did not consistently include them in their work. This is the list of articles that would be removed: _der_, _die_, _das_, _den_, _dem_, _des_, _d._ (abbreviation), _ein_, _eine_, _einen_, _einem_, _einer_, _eines_. Note that if an article appeared within an annotation but not at its very beginning, it would not cause a change. 
     * Remove full stops in the end of an annotation: If last character is a full stop and the annotation text's length is maximum 5, consider it as an abbreviation and remove the full stop.
4. The annotation indices produced by doccano can be odd, so they are cleared.
   * Some annotations were not given a label.
   * Some annotations would have `start` or `end` indices that are larger than the length of the document/text they can refer to. This is impossible and was automatically removed after inspection during development time. You would want to set a breakpoint there for your own dataset.
   * Some annotations did not contain any characters, i.e. `start == end`.
   * Suspiciously long annotations with &get; 100 characters are stored to a CSV, the user can manually indicate in the last column, whether they should be removed. This requires editing the CSV as indicated in the console before starting the next step.
   * Now, `4a` **awaits user input before continuing with** `4b`.
   * `4b` removes those lines the user did not want to keep. Default is that annotations are kept.
5. 

