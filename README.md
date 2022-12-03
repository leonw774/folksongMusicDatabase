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

Read the doc string in `database.py` for database detail.

### Search the database by content (melody)

For now, the search function only receive music query in json with certain format.

```
python3 ./search.py path/to/database/pickled/file path/to/query/json/file
```

### Do expriment

First we make the four databases of different parameter sets

-  `python3 .\make_database.py dataset md_old.pickle --old`
-  `python3 .\make_database.py dataset md_alpha0.0.pickle -a 0.0`
-  `python3 .\make_database.py dataset md_alpha0.3.pickle -a 0.3`
-  `python3 .\make_database.py dataset md_alpha1.0.pickle -a 1.0`

And then for all four databases, we input five different corruption numbers

`python3 .\get_experiment_data.py dataset $DATABASE_FILE -c $CORRUPTION_NUMBER`

We will collect three values in experiment result (Detail in experiment report)

- Average precision
- Note-tuple corruption hit rate
- Jianpu corruption hit rate

Run the shell script `run_experiments.sh` to collect all data
