from typing import List
from zipfile import ZipFile

from project_paths import *

print("Unzipping archive exported from doccano")
print(f"- Data is located at '{DATA_DIR}'")

latestZip = [file for file in os.listdir(DATA_DIR)
             if file.endswith('.zip')]
latestZip.sort(reverse=True)
latestZip = latestZip[0]
latestZip = os.path.join(DATA_DIR, latestZip)
print(f"- Chose '{latestZip}' to be unzipped")

with ZipFile(latestZip) as zipfile:
    zipfile.extractall(DATA_DIR)
del latestZip, zipfile
print("- unzipping finished")
