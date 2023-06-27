import os

DATA_DIR = os.path.join(os.path.curdir, os.path.pardir, 'data')
DATA_DIR = os.path.abspath(DATA_DIR)

RAW_DATA_DIR = os.path.join(DATA_DIR, '0-raw')

if __name__ == '__main__':
    print(DATA_DIR,
          RAW_DATA_DIR, sep="\n")
