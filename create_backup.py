#####
# Author: brvn0 <me@brvn0.de>
# Date: 2022-10-24
# Version: 1.0
#####


import os
import time
import shutil
import argparse
import sys

sys.setrecursionlimit(10000)


def ignorePath(path):
    def ignoref(directory, contents):
        return (f for f in contents if os.path.abspath(os.path.join(directory, f)) == path)
    return ignoref


def backup(INPUT_DIR, OUTPUT_DIR, TMP, PGP_PATH=None, ALGORITHM="lz4"):
    # TODO implement pgp encrypting
    OUTPUT_FILE = OUTPUT_DIR + "/" + \
        time.strftime("%Y%m%d") + \
        ".tar.{ALGORITHM}".format(ALGORITHM=ALGORITHM)
    # Create a backup of INPUT directory
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    shutil.copytree(INPUT_DIR, TMP, ignore=shutil.ignore_patterns(
        '*.tar.lz4', '.tmp', 'backups'))
    # tar.lz4 compress the backup
    os.system(
        "tar cf - {TMP} | {ALGORITHM} > {OUTPUT_FILE}".format(TMP=TMP, ALGORITHM=ALGORITHM, OUTPUT_FILE=OUTPUT_FILE))
    # delete the temporary backup
    shutil.rmtree(TMP)
    return OUTPUT_FILE


def copyMssqlDb(INPUT, OUTPUT):
    # delete old copy if exists
    if os.path.exists(OUTPUT):
        shutil.rmtree(OUTPUT)
    # Copy the database
    shutil.copytree(INPUT, OUTPUT)


def main():
    # Copy the mssql database to the smb share
    if args.noMssql:
        print("Skipping MSSQL DB for {user}".format(user=user))
    else:
        mssqlStart = time.perf_counter()
        copyMssqlDb(ORIGIN_MSSQL_DIR, TARGET_MSSQL_DIR)
        mssqlEnd = time.perf_counter()
        print("MSSQL DB for {user} copied in: ".format(user=user) +
              str(int(round(mssqlEnd - mssqlStart, 0))) + " seconds")

    # Create a backup of the Samba share
    backUpStart = time.perf_counter()
    outfile = backup(IN_DIR, OUT_DIR, TMP_DIR, None)
    backUpEnd = time.perf_counter()
    print("Backup for {user} created in: ".format(user=user) +
          str(round(backUpEnd - backUpStart, 0)) + " seconds (or ca. " + str(int(round((backUpEnd - backUpStart) / 60, 0))) + " Minutes)\nOutfile: {outfile}".format(outfile=outfile))


def getArgs(performChecks=False):
    parser = argparse.ArgumentParser(
        description='Create a backup of the user\'s data.', epilog='Forgive me for the poor style of coding here but this isn\'t meant to be used by anyone who is\'nt myself because it\'s made for a very special use case.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('user', metavar='USER', type=str, action='store',
                        nargs=1, help='The user to backup')
    # add an argument to specify the compression algorithm
    parser.add_argument('-c', '--compression-algorithm', dest='compressionAlgorithm', metavar='ALGORITHM', type=str,
                        nargs=1, default="lz4", help='The compression algorithm to use; Default: lz4; The compression algorithm must be installed on the system!!!')
    parser.add_argument('-m', '--no-mssql', dest='noMssql', action='store_true',
                        default=False, help='Don\'t copy the mssql database to the users samba share AND don\'t include the mssql database snapshot in the users samba share into the backup')
    # add an argument to use a test directory
    parser.add_argument('-t', '--test', dest='test', metavar=('IN', 'OUT'), action='store', nargs=2,
                        help='Use a set of in and out dir so we dont use the production samba share; 1. IN: The input directory; 2. OUT: The output directory (NOT file -> is named automatically)')

    args = parser.parse_args()

    if args.test == None:
        args.test = False

    # just some checks to make sure the user exists
    if performChecks:
        # check if the user's samba share exists
        if not os.path.exists(IN_DIR.format(user=args.user[0]) + "-priv" if args.user[0] != "public" else IN_DIR.format(user=args.user[0])):
            print("The user's samba share doesn't exist!")
            exit(1)

        # check if the user's mssql database exists
        if not os.path.exists(ORIGIN_MSSQL_DIR.format(user=args.user[0])) and not args.noMssql:
            print("The user's mssql database doesn't exist!")
            exit(1)

    return args


def resetPerms(dirs):
    for dir in dirs:
        os.system("chown -R {user}:kanzlei {dir}".format(user=user, dir=dir))
        os.system("chmod -R 777 {dir}".format(dir=dir))
    print('Ensured permissions for {user}'.format(user=user))


# checks for disable file in user dir
def checkForDisableFile(files):
    if "DISABLE_BACKUP" in files:
        print("Found DISABLED file. Aborting.")
        exit(0)


#####
# CONFIG
#####
IN_DIR = "/data/smb/{user}"
OUT_DIR = "/backups/{user}"
TMP_DIR = "{OUT_DIR}/.tmp"
ORIGIN_MSSQL_DIR = "/data/mssql/{user}"
TARGET_MSSQL_DIR = "{IN_DIR}/mssql"

if __name__ == "__main__":
    args = getArgs()
    user = args.user[0]

    if not args.test:
        IN_DIR = IN_DIR.format(user=user)
        OUT_DIR = OUT_DIR.format(user=user)
    else:
        IN_DIR = args.test[0]
        OUT_DIR = args.test[1]
        args.noMssql = True

    TMP_DIR = TMP_DIR.format(OUT_DIR=OUT_DIR)
    ORIGIN_MSSQL_DIR = ORIGIN_MSSQL_DIR.format(user=user)
    TARGET_MSSQL_DIR = TARGET_MSSQL_DIR.format(IN_DIR=IN_DIR)

    main()
    resetPerms([OUT_DIR, TARGET_MSSQL_DIR])
