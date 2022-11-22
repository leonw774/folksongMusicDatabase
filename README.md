# folksongMusicDatabase

## Depedency

- Python >= 3.7
  - tqdm

## Dataset

Download all 21 files from http://www.esac-data.org/data/ into a single directory.

## Usage

### Make database

```
python3 ./make_database.py path/to/dataset/directory path/to/output/pickled/file
```

The script will process all the records, and dumps the database's object into a python pickle file.

Read the doc string in `databaase.py` for database detail.

### Search the database by content

For now, the search function only receive music query in json with certain format.

```
python3 ./search.py path/to/database/pickled/file path/to/query/json/file
```

### Do expriment

```
python3 ./experiment.py path/to/database/pickled/file -c NUMBER_OF_CORRUPTION -n NUMBER_OF_TEST
```
