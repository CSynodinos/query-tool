# Regex Query Tool
A Python query tool using regex to identify and store user specified file patterns.

## Authors
[CSynodinos](https://github.com/CSynodinos)

## Description
This tool is capable of identifying user specified patterns in text and spreadsheet files. The file types that are currently supported are: 
* .txt
* .ini
* .fasta
* .csv
* .tsv

## Example
```bash
    >>> query.py -f ["your_file"] -p ["your_pattern"]

    To see all the options available:
    >>> query.py -h
```

## Database integration

All patterns identified can be stored into a .json file regardless of the input file type, by using the -json argument.The json file gets the same name as the input file. If the -json option is used, the database options become functional. By using the -db option, the -json file will be saved in an sqlite3 type database that will be automatically generated. If the -pg option is used with the -db option, the database is instead a postgres 4 database.

Currently, only sqlite3 and postgres 4 are supported. Appending the patterns to an existing database of the same type is not supported at the current version of the tool. The aim for next version of the tool is to support such features.

