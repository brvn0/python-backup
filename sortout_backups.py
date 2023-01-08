#####
# Author: brvn0 <me@brvn0.de>
# Date: 2022-10-24
# Version: 1.0
#####


import argparse
from datetime import datetime, date, timedelta
import re
import os
import time

BASEDIR = "/backups/{user}"


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# generate test file list
# format: yyyymmdd.tar.lz4
# example: 20180101.tar.lz4
def generateDemoFiles():
    start_date = date(2022, 3, 1)
    end_date = date(2022, 10, 23)

    fileNames = []
    for single_date in daterange(start_date, end_date):
        fileNames.append(single_date.strftime("%Y%m%d.tar.lz4"))
    return fileNames


# DONT FUCKING TOUCH THIS
# IT WORKS RN AND I NOR ANYONE ELSE WILL TOUCH IT
# IF YOU TOUCH IT YOU WILL BE FIRED
# AND I WILL FIND YOU
# HOURS USE D TO GET THIS SHIT TO WORK: 3
def sortOut(fileNames):
    toDelete = []
    # topPerMonths = {}
    for file in fileNames:
        name = re.split("([0-9]{8})", file)
        if args.verbose:
            print("name: " + name[1])
        try:
            name = name[1]
        except IndexError:
            print("Skipping file -> IndexError (date not found in name): " + file)
            continue
        # date object from string
        date = datetime.strptime(name, "%Y%m%d")

        if (date < datetime.now() - timedelta(days=30)) or (
            date < datetime.now() - timedelta(days=7) and date.weekday() != 4
        ):
            toDelete.append(file)
            if args.verbose:
                print("toDelete: " + file)
            continue

    #     if date < datetime.now() - timedelta(days=60):
    #         if date.strftime("%Y%m") in topPerMonths:
    #             if topPerMonths[str(date.strftime("%Y%m"))] < date:
    #                 toDelete.append(
    #                     topPerMonths[str(date.strftime("%Y%m"))].strftime(
    #                         "%Y%m%d.tar.lz4"
    #                     )
    #                 )
    #                 topPerMonths[str(date.strftime("%Y%m"))] = date
    #             else:
    #                 toDelete.append(file)
    #                 if args.verbose:
    #                     print("toDelete: " + file)
    #         else:
    #             topPerMonths[str(date.strftime("%Y%m"))] = date

    # for top in topPerMonths:
    #     # remove month tops frn toDelete
    #     try:
    #         toDelete.remove(topPerMonths[top].strftime("%Y%m%d.tar.lz4"))
    #     except ValueError:
    #         # The top of a month isn't in the toDelete list so we don't have to worry about it
    #         pass

    toDelete = sorted(set(toDelete))
    return toDelete


# checks for disable file in user dir
def checkForDisableFile(files):
    if "DISABLE_SORTOUT" in files:
        print("Found DISABLED file. Aborting.")
        exit(0)


parser = argparse.ArgumentParser(
    description="Sort out the backups of the user's data.\nBase Dir: {BASEDIR}".format(
        BASEDIR=BASEDIR
    )
)
parser.add_argument("user", help="The user's name")
parser.add_argument(
    "-t",
    "--test",
    action="store_true",
    help="Test/Demo mode; Parses a pre-defined list of filenames and prints the result",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Verbose mode; Prints more information"
)
parser.add_argument(
    "-g",
    "--generate",
    nargs=1,
    metavar="PATH",
    help="Generates a couple of empty demo files",
    action="store",
)
parser.add_argument(
    "-d", "--dry-run", action="store_true", help="Dry run; Does not delete anything"
)
parser.add_argument(
    "-p", "--path", action="store", nargs=1, help="Path to the backup directory"
)
args = parser.parse_args()

if args.generate:
    for file in generateDemoFiles():  # type: ignore
        f = open(args.generate[0] + "/" + file, "w")
        f.write("This is a demo file")
        f.close()
    exit(0)

if args.test:
    fileNames = generateDemoFiles()
    print("Test/Demo mode")
else:
    BASEDIR = BASEDIR.format(user=args.user)
    if args.verbose:
        print("BASEDIR: {BASEDIR}".format(BASEDIR=BASEDIR))

    # get all files in BASEDIR
    fileNames = os.listdir(BASEDIR)

if args.verbose:
    print("generated file list: {fileNames}".format(fileNames=fileNames))

checkForDisableFile(fileNames)

toDelete = sortOut(fileNames)
print(
    "still existing files: {existingFiles}".format(
        existingFiles=str(sorted(set(fileNames).difference(set(toDelete))))
    )
)


# delete files
if args.dry_run:
    print("Dry run; Not deleting anything")
else:
    timeStart = time.time()
    for file in toDelete:
        if args.verbose:
            print("deleting: {file}".format(file=file))
        os.remove(BASEDIR + "/" + file)
    endTime = time.time() - timeStart
    print(
        "deleted {count} files in {time} seconds".format(
            count=len(toDelete), time=round(endTime, 2)
        )
    )


exit(0)
