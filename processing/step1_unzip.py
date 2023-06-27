from zipfile import ZipFile

from project_paths import *

INPUT_DIR = RAW_DATA_DIR
OUTPUT_DIR = os.path.join(DATA_DIR, '1-unzip')

print("Processing Step 1: Unzipping archive exported from doccano")
print(f"- Data is generally located at '{DATA_DIR}'")
print(f"- Raw data is located at '{INPUT_DIR}'")

latestZip = [file for file in os.listdir(INPUT_DIR)
             if file.endswith('.zip')]
latestZip.sort(reverse=True)
latestZip = latestZip[0]
latestZip = os.path.join(INPUT_DIR, latestZip)
print(f"- Chose '{latestZip}' to be unzipped")

with ZipFile(latestZip) as zipfile:
    zipfile.extractall(OUTPUT_DIR)
del latestZip, zipfile
print("- unzipping finished")
