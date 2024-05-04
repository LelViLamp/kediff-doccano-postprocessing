"""
Honestly, I just did not know where else to put these functions, so here
they are in a classic utils/misc/helper dump. Do enjoy
"""
import os.path


def extract_annotator_name(
        path_or_filename: str,
        extension: str = ""
) -> str:
    # if no extension provided, identify it automatically
    if extension == "":
        extension = path_or_filename.split(".")[-1]
    if not extension.startswith("."):
        extension = f".{extension}"

    filename: str
    filename = path_or_filename.split(os.path.sep)[-1]
    filename = filename.removesuffix(extension)

    return filename
    # end def


def main():
    annotator_name = extract_annotator_name("text/name.tar.gz", "tar.gz")
    print(annotator_name)
    # end def


if __name__ == "__main__":
    main()
