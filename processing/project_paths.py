import os

DATA_DIR: str = os.path.join(os.path.curdir, os.path.pardir, 'data')
DATA_DIR = os.path.abspath(DATA_DIR)
RAW_DATA_DIR: str = os.path.join(DATA_DIR, '0-raw')

print(
    DATA_DIR,
    RAW_DATA_DIR,
    sep="\n"
)
