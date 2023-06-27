from zipfile import ZipFile

from project_paths import *

OUTPUT_DIR = os.path.join(DATA_DIR, '1-unzip')

print("Processing Step 1: Unzipping archive exported from doccano")
print(f"- Data is located at '{DATA_DIR}'")
print(f"- Raw data is located at '{RAW_DATA_DIR}'")

latestZip = [file for file in os.listdir(RAW_DATA_DIR)
             if file.endswith('.zip')]
latestZip.sort(reverse=True)
latestZip = latestZip[0]
latestZip = os.path.join(RAW_DATA_DIR, latestZip)
print(f"- Chose '{latestZip}' to be unzipped")

with ZipFile(latestZip) as zipfile:
    zipfile.extractall(OUTPUT_DIR)
del latestZip, zipfile
print("- unzipping finished")
