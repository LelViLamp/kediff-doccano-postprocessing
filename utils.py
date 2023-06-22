"""
Honestly, I just did not know where else to put these functions, so here
they are in a classic utils/misc/helper dump. Do enjoy
"""
import os.path


def extract_annotator_name(path_or_filename: str,
                           extension: str = "") -> str:
    if extension == "":
        extension = path_or_filename.split(".")[-1]
    if not extension.startswith("."):
        extension = f".{extension}"

    filename = path_or_filename.split(os.path.sep)[-1]
    filename = filename.removesuffix(extension)

    return filename


if __name__ == "__main__":
    annotator_name = extract_annotator_name("text/name.tar.gz", "tar.gz")
    print(annotator_name)