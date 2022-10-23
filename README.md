A backup is sorted out if

1. older than 14 days and not from a friday
2. older than 90 days and not the latest from its month
3. older 180 days

backups can be created with tar -> and any algorithm installed on the system (i only test lz4!)
backups are named YYYYmmdd.tar.lz4 (20221024.tar.lz4)

## Usage

```bash
~$ python3 ./create_backup.py -h
usage: create_backup.py [-h] [-c ALGORITHM] [-m] [-t IN OUT] USER

Create a backup of the users data.

positional arguments:
  USER                  The user to backup

options:
  -h, --help            show this help message and exit
  -c ALGORITHM, --compression-algorithm ALGORITHM
                        The compression algorithm to use; Default: lz4; The compression algorithm must be installed on the system!!!
  -m, --no-mssql        Dont copy the mssql database to the users samba share AND dont include the mssql database snapshot in the users samba share into the backup
  -t IN OUT, --test IN OUT
                        Use a set of in and out dir so we dont use the production samba share; 1. IN: The input directory; 2. OUT: The output directory (NOT file -> is named automatically)

Forgive me for the poor style of coding here but this isnt meant to be used by anyone who isnt myself because its made for a very special use case.
```

```bash
~$ python3 ./restore_backup.py -h
usage: sortout_backups.py [-h] [-t] [-v] [-g PATH] [-d] [-p PATH] user

Sort out the backups of the users data. Base Dir: /data/smb/{user}

positional arguments:
  user                  The users name

options:
  -h, --help            show this help message and exit
  -t, --test            Test/Demo mode; Parses a pre-defined list of filenames and prints the result
  -v, --verbose         Verbose mode; Prints more information
  -g PATH, --generate PATH
                        Generates a couple of empty demo files
  -d, --dry-run         Dry run; Does not delete anything
  -p PATH, --path PATH  Path to the backup directory
```
